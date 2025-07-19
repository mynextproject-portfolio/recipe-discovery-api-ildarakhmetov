from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
import sqlite3
import json
from json import JSONDecodeError, JSONEncoder
import httpx
import asyncio
import redis
import logging

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)

# Redis Cache Service
class RedisCache:
    """Service for Redis caching operations."""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.redis_url = redis_url
        self._client = None
    
    def _get_client(self):
        """Get Redis client, creating it if it doesn't exist."""
        if self._client is None:
            try:
                self._client = redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                self._client.ping()
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logging.warning(f"Redis connection failed: {e}. Caching will be disabled.")
                self._client = None
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        client = self._get_client()
        if client is None:
            return None
        
        try:
            return client.get(key)
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.warning(f"Redis get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> bool:
        """Set value in cache with TTL (default 24 hours)."""
        client = self._get_client()
        if client is None:
            return False
        
        try:
            return client.setex(key, ttl_seconds, value)
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.warning(f"Redis set failed for key {key}: {e}")
            return False

# Singleton cache instance
_cache_instance: Optional[RedisCache] = None

def get_cache() -> RedisCache:
    """Get Redis cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance

# Unified Recipe model
class Recipe(BaseModel):
    id: Optional[int] = None
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str
    source: str = "internal"  # Default to internal for existing recipes

# Request model for creating/updating recipes (without ID)
class RecipeRequest(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str

# Response model (Recipe with ID)
class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str
    source: str

# MealDB API Service
class MealDBService:
    """Service for interacting with TheMealDB API with Redis caching."""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    CACHE_TTL = 86400  # 24 hours in seconds
    
    @staticmethod
    async def search_meals(query: str) -> List[Recipe]:
        """Search for meals by name from TheMealDB API with Redis caching."""
        if not query:
            return []
        
        # Create cache key including the search query
        cache_key = f"mealdb:search:{query.lower().strip()}"
        cache = get_cache()
        
        # Try to get from cache first
        cached_result = await cache.get(cache_key)
        if cached_result:
            try:
                # Deserialize cached recipes
                cached_data = json.loads(cached_result)
                recipes = []
                for recipe_data in cached_data:
                    recipe = Recipe(**recipe_data)
                    recipes.append(recipe)
                return recipes
            except (JSONDecodeError, TypeError) as e:
                logging.warning(f"Failed to deserialize cached data for key {cache_key}: {e}")
                # Continue to fetch from API if cache is corrupted
        
        # Cache miss - fetch from MealDB API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{MealDBService.BASE_URL}/search.php", params={"s": query})
                response.raise_for_status()
                data = response.json()
                
                if not data.get("meals"):
                    # Cache empty results too to avoid repeated API calls for non-existent recipes
                    await cache.set(cache_key, json.dumps([]), MealDBService.CACHE_TTL)
                    return []
                
                recipes = []
                for meal in data["meals"]:
                    recipe = MealDBService._transform_meal_to_recipe(meal)
                    recipes.append(recipe)
                
                # Cache the results
                try:
                    recipes_data = [recipe.model_dump() for recipe in recipes]
                    await cache.set(cache_key, json.dumps(recipes_data), MealDBService.CACHE_TTL)
                except (TypeError, Exception) as e:
                    logging.warning(f"Failed to cache recipes for key {cache_key}: {e}")
                
                return recipes
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            # Log error in production, for now return empty list to not break search
            logging.error(f"Error fetching from MealDB: {e}")
            return []
    
    @staticmethod
    def _transform_meal_to_recipe(meal: dict) -> Recipe:
        """Transform MealDB meal data to our Recipe format."""
        # Extract ingredients and measurements
        ingredients = []
        for i in range(1, 21):  # MealDB has up to 20 ingredients
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            
            if ingredient and ingredient.strip():
                if measure and measure.strip():
                    ingredients.append(f"{measure.strip()} {ingredient.strip()}")
                else:
                    ingredients.append(ingredient.strip())
        
        # Split instructions into steps
        instructions = meal.get("strInstructions", "")
        steps = [step.strip() for step in instructions.split("\r\n") if step.strip()]
        if not steps:
            steps = [instructions] if instructions else ["No instructions available"]
        
        return Recipe(
            id=meal.get("idMeal"),
            title=meal.get("strMeal", "Unknown Recipe"),
            ingredients=ingredients,
            steps=steps,
            prepTime="Unknown",  # MealDB doesn't provide prep time
            cookTime="Unknown",  # MealDB doesn't provide cook time
            difficulty="Unknown",  # MealDB doesn't provide difficulty
            cuisine=meal.get("strArea", "Unknown"),
            source="mealdb"
        )

# Abstract Repository Interface
class RecipeRepository(ABC):
    """Abstract base class for recipe data operations."""
    
    @abstractmethod
    def get_all(self) -> List[Recipe]:
        """Get all recipes."""
        pass
    
    @abstractmethod
    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        pass
    
    @abstractmethod
    def search_by_title(self, query: str) -> List[Recipe]:
        """Search recipes by title substring."""
        pass
    
    @abstractmethod
    def create(self, recipe_request: RecipeRequest) -> Recipe:
        """Create a new recipe."""
        pass
    
    @abstractmethod
    def update(self, recipe_id: int, recipe_request: RecipeRequest) -> Optional[Recipe]:
        """Update an existing recipe."""
        pass

# Concrete In-Memory Implementation
class InMemoryRecipeRepository(RecipeRepository):
    """In-memory implementation of recipe repository."""
    
    def __init__(self):
        # Sample data
        self._recipes: List[Recipe] = [
            Recipe(
                id=1,
                title="Classic Chocolate Chip Cookies",
                ingredients=[
                    "2 1/4 cups all-purpose flour",
                    "1 tsp baking soda",
                    "1 tsp salt",
                    "1 cup butter, softened",
                    "3/4 cup granulated sugar",
                    "3/4 cup brown sugar",
                    "2 large eggs",
                    "2 tsp vanilla extract",
                    "2 cups chocolate chips"
                ],
                steps=[
                    "Preheat oven to 375°F (190°C)",
                    "Mix flour, baking soda, and salt in a bowl",
                    "Cream butter and sugars until fluffy",
                    "Beat in eggs and vanilla",
                    "Gradually mix in flour mixture",
                    "Stir in chocolate chips",
                    "Drop rounded tablespoons onto ungreased baking sheet",
                    "Bake 9-11 minutes until golden brown",
                    "Cool on baking sheet for 2 minutes, then transfer to wire rack"
                ],
                prepTime="15 minutes",
                cookTime="10 minutes",
                difficulty="easy",
                cuisine="American"
            ),
            Recipe(
                id=2,
                title="Spaghetti Carbonara",
                ingredients=[
                    "400g spaghetti",
                    "200g pancetta or guanciale, diced",
                    "4 large eggs",
                    "100g Pecorino Romano cheese, grated",
                    "Black pepper to taste",
                    "Salt for pasta water"
                ],
                steps=[
                    "Bring a large pot of salted water to boil",
                    "Cook spaghetti according to package directions",
                    "Meanwhile, cook pancetta in a large skillet until crispy",
                    "In a bowl, whisk eggs with grated cheese and black pepper",
                    "Reserve 1 cup pasta water, then drain pasta",
                    "Add hot pasta to skillet with pancetta",
                    "Remove from heat and quickly stir in egg mixture",
                    "Add pasta water as needed to create creamy sauce",
                    "Serve immediately with extra cheese and pepper"
                ],
                prepTime="10 minutes",
                cookTime="15 minutes",
                difficulty="medium",
                cuisine="Italian"
            ),
            Recipe(
                id=3,
                title="Chicken Tikka Masala",
                ingredients=[
                    "1 lb chicken breast, cubed",
                    "1 cup plain yogurt",
                    "2 tbsp tikka masala spice blend",
                    "1 onion, diced",
                    "3 cloves garlic, minced",
                    "1 inch ginger, grated",
                    "1 can crushed tomatoes",
                    "1 cup heavy cream",
                    "2 tbsp vegetable oil",
                    "Salt to taste",
                    "Fresh cilantro for garnish"
                ],
                steps=[
                    "Marinate chicken in yogurt and half the spice blend for 30 minutes",
                    "Heat oil in a large pan over medium-high heat",
                    "Cook marinated chicken until golden, then set aside",
                    "In same pan, sauté onion until soft",
                    "Add garlic, ginger, and remaining spices, cook 1 minute",
                    "Add tomatoes and simmer 10 minutes",
                    "Stir in cream and return chicken to pan",
                    "Simmer 10-15 minutes until chicken is cooked through",
                    "Garnish with cilantro and serve with rice"
                ],
                prepTime="45 minutes",
                cookTime="30 minutes",
                difficulty="medium",
                cuisine="Indian"
            ),
            Recipe(
                id=4,
                title="Caesar Salad",
                ingredients=[
                    "1 large head romaine lettuce, chopped",
                    "1/2 cup Parmesan cheese, grated",
                    "1/4 cup croutons",
                    "2 anchovy fillets (optional)",
                    "2 cloves garlic",
                    "1/4 cup mayonnaise",
                    "2 tbsp lemon juice",
                    "1 tsp Worcestershire sauce",
                    "1/4 tsp black pepper"
                ],
                steps=[
                    "Wash and dry romaine lettuce thoroughly",
                    "Make dressing by mashing garlic and anchovies",
                    "Whisk in mayonnaise, lemon juice, and Worcestershire",
                    "Season with black pepper",
                    "Toss lettuce with dressing",
                    "Top with Parmesan cheese and croutons",
                    "Serve immediately"
                ],
                prepTime="15 minutes",
                cookTime="0 minutes",
                difficulty="easy",
                cuisine="Italian"
            )
        ]
        self._next_id = 5
    
    def get_all(self) -> List[Recipe]:
        """Get all recipes."""
        return [recipe for recipe in self._recipes if recipe.id is not None]
    
    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        for recipe in self._recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def search_by_title(self, query: str) -> List[Recipe]:
        """Search recipes by title substring (case-insensitive)."""
        if not query:
            return []
        
        query_lower = query.lower()
        return [
            recipe for recipe in self._recipes 
            if recipe.id is not None and query_lower in recipe.title.lower()
        ]
    
    def create(self, recipe_request: RecipeRequest) -> Recipe:
        """Create a new recipe."""
        recipe = Recipe(**recipe_request.model_dump(), id=self._next_id)
        self._recipes.append(recipe)
        self._next_id += 1
        return recipe
    
    def update(self, recipe_id: int, recipe_request: RecipeRequest) -> Optional[Recipe]:
        """Update an existing recipe."""
        for i, recipe in enumerate(self._recipes):
            if recipe.id == recipe_id:
                updated_recipe = Recipe(**recipe_request.model_dump(), id=recipe_id)
                self._recipes[i] = updated_recipe
                return updated_recipe
        return None

# Concrete SQLite Implementation
class SQLiteRecipeRepository(RecipeRepository):
    """SQLite implementation of recipe repository."""
    
    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        self._init_database()
        self._seed_sample_data()
    
    def _init_database(self):
        """Initialize the SQLite database and create tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    prepTime TEXT NOT NULL,
                    cookTime TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    cuisine TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def _seed_sample_data(self):
        """Add sample data if the database is empty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert the same sample data as InMemoryRecipeRepository
                sample_recipes = [
                    (1, "Classic Chocolate Chip Cookies", 
                     '["2 1/4 cups all-purpose flour", "1 tsp baking soda", "1 tsp salt", "1 cup butter, softened", "3/4 cup granulated sugar", "3/4 cup brown sugar", "2 large eggs", "2 tsp vanilla extract", "2 cups chocolate chips"]',
                     '["Preheat oven to 375°F (190°C)", "Mix flour, baking soda, and salt in a bowl", "Cream butter and sugars until fluffy", "Beat in eggs and vanilla", "Gradually mix in flour mixture", "Stir in chocolate chips", "Drop rounded tablespoons onto ungreased baking sheet", "Bake 9-11 minutes until golden brown", "Cool on baking sheet for 2 minutes, then transfer to wire rack"]',
                     "15 minutes", "10 minutes", "easy", "American"),
                    
                    (2, "Spaghetti Carbonara",
                     '["400g spaghetti", "200g pancetta or guanciale, diced", "4 large eggs", "100g Pecorino Romano cheese, grated", "Black pepper to taste", "Salt for pasta water"]',
                     '["Bring a large pot of salted water to boil", "Cook spaghetti according to package directions", "Meanwhile, cook pancetta in a large skillet until crispy", "In a bowl, whisk eggs with grated cheese and black pepper", "Reserve 1 cup pasta water, then drain pasta", "Add hot pasta to skillet with pancetta", "Remove from heat and quickly stir in egg mixture", "Add pasta water as needed to create creamy sauce", "Serve immediately with extra cheese and pepper"]',
                     "10 minutes", "15 minutes", "medium", "Italian"),
                    
                    (3, "Chicken Tikka Masala",
                     '["1 lb chicken breast, cubed", "1 cup plain yogurt", "2 tbsp tikka masala spice blend", "1 onion, diced", "3 cloves garlic, minced", "1 inch ginger, grated", "1 can crushed tomatoes", "1 cup heavy cream", "2 tbsp vegetable oil", "Salt to taste", "Fresh cilantro for garnish"]',
                     '["Marinate chicken in yogurt and half the spice blend for 30 minutes", "Heat oil in a large pan over medium-high heat", "Cook marinated chicken until golden, then set aside", "In same pan, sauté onion until soft", "Add garlic, ginger, and remaining spices, cook 1 minute", "Add tomatoes and simmer 10 minutes", "Stir in cream and return chicken to pan", "Simmer 10-15 minutes until chicken is cooked through", "Garnish with cilantro and serve with rice"]',
                     "45 minutes", "30 minutes", "medium", "Indian"),
                    
                    (4, "Caesar Salad",
                     '["1 large head romaine lettuce, chopped", "1/2 cup Parmesan cheese, grated", "1/4 cup croutons", "2 anchovy fillets (optional)", "2 cloves garlic", "1/4 cup mayonnaise", "2 tbsp lemon juice", "1 tsp Worcestershire sauce", "1/4 tsp black pepper"]',
                     '["Wash and dry romaine lettuce thoroughly", "Make dressing by mashing garlic and anchovies", "Whisk in mayonnaise, lemon juice, and Worcestershire", "Season with black pepper", "Toss lettuce with dressing", "Top with Parmesan cheese and croutons", "Serve immediately"]',
                     "15 minutes", "0 minutes", "easy", "Italian")
                ]
                
                cursor.executemany("""
                    INSERT INTO recipes (id, title, ingredients, steps, prepTime, cookTime, difficulty, cuisine)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_recipes)
                
                # Set the auto-increment counter to start at 5
                cursor.execute("UPDATE sqlite_sequence SET seq = 4 WHERE name = 'recipes'")
                conn.commit()
    
    def _dict_factory(self, cursor, row):
        """Convert SQLite row to dictionary."""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    def get_all(self) -> List[Recipe]:
        """Get all recipes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes ORDER BY id")
            rows = cursor.fetchall()
            
            recipes = []
            for row in rows:
                recipe = Recipe(
                    id=row['id'],
                    title=row['title'],
                    ingredients=json.loads(row['ingredients']),
                    steps=json.loads(row['steps']),
                    prepTime=row['prepTime'],
                    cookTime=row['cookTime'],
                    difficulty=row['difficulty'],
                    cuisine=row['cuisine']
                )
                recipes.append(recipe)
            return recipes
    
    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            row = cursor.fetchone()
            
            if row:
                return Recipe(
                    id=row['id'],
                    title=row['title'],
                    ingredients=json.loads(row['ingredients']),
                    steps=json.loads(row['steps']),
                    prepTime=row['prepTime'],
                    cookTime=row['cookTime'],
                    difficulty=row['difficulty'],
                    cuisine=row['cuisine']
                )
            return None
    
    def search_by_title(self, query: str) -> List[Recipe]:
        """Search recipes by title substring (case-insensitive)."""
        if not query:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE title LIKE ? ORDER BY id", (f"%{query}%",))
            rows = cursor.fetchall()
            
            recipes = []
            for row in rows:
                recipe = Recipe(
                    id=row['id'],
                    title=row['title'],
                    ingredients=json.loads(row['ingredients']),
                    steps=json.loads(row['steps']),
                    prepTime=row['prepTime'],
                    cookTime=row['cookTime'],
                    difficulty=row['difficulty'],
                    cuisine=row['cuisine']
                )
                recipes.append(recipe)
            return recipes
    
    def create(self, recipe_request: RecipeRequest) -> Recipe:
        """Create a new recipe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recipes (title, ingredients, steps, prepTime, cookTime, difficulty, cuisine)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_request.title,
                json.dumps(recipe_request.ingredients),
                json.dumps(recipe_request.steps),
                recipe_request.prepTime,
                recipe_request.cookTime,
                recipe_request.difficulty,
                recipe_request.cuisine
            ))
            
            recipe_id = cursor.lastrowid
            conn.commit()
            
            return Recipe(
                id=recipe_id,
                title=recipe_request.title,
                ingredients=recipe_request.ingredients,
                steps=recipe_request.steps,
                prepTime=recipe_request.prepTime,
                cookTime=recipe_request.cookTime,
                difficulty=recipe_request.difficulty,
                cuisine=recipe_request.cuisine
            )
    
    def update(self, recipe_id: int, recipe_request: RecipeRequest) -> Optional[Recipe]:
        """Update an existing recipe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if recipe exists
            cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
            if not cursor.fetchone():
                return None
            
            cursor.execute("""
                UPDATE recipes 
                SET title = ?, ingredients = ?, steps = ?, prepTime = ?, cookTime = ?, difficulty = ?, cuisine = ?
                WHERE id = ?
            """, (
                recipe_request.title,
                json.dumps(recipe_request.ingredients),
                json.dumps(recipe_request.steps),
                recipe_request.prepTime,
                recipe_request.cookTime,
                recipe_request.difficulty,
                recipe_request.cuisine,
                recipe_id
            ))
            
            conn.commit()
            
            return Recipe(
                id=recipe_id,
                title=recipe_request.title,
                ingredients=recipe_request.ingredients,
                steps=recipe_request.steps,
                prepTime=recipe_request.prepTime,
                cookTime=recipe_request.cookTime,
                difficulty=recipe_request.difficulty,
                cuisine=recipe_request.cuisine
            )

# Singleton repository instance
_repository_instance: Optional[RecipeRepository] = None

# Dependency Injection
def get_recipe_repository() -> RecipeRepository:
    """Dependency injection function for recipe repository."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = SQLiteRecipeRepository()
    return _repository_instance

@app.get("/ping")
def ping():
    """Health check endpoint to verify the service is running."""
    # Hot reloading test - this change should be picked up automatically
    return "pong"

@app.get("/recipes", response_model=List[RecipeResponse])
def get_all_recipes(repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get all available recipes."""
    recipes = repository.get_all()
    return [RecipeResponse(**recipe.model_dump()) for recipe in recipes]

@app.get("/recipes/search", response_model=List[RecipeResponse])
async def search_recipes(q: Optional[str] = None, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Search recipes by title using substring matching (case-insensitive) from both internal database and MealDB API."""
    if not q:
        return []
    
    # Search both internal recipes and MealDB simultaneously
    internal_recipes_task = asyncio.create_task(asyncio.to_thread(repository.search_by_title, q))
    mealdb_recipes_task = asyncio.create_task(MealDBService.search_meals(q))
    
    # Wait for both searches to complete
    internal_recipes, mealdb_recipes = await asyncio.gather(internal_recipes_task, mealdb_recipes_task)
    
    # Combine results
    all_recipes = internal_recipes + mealdb_recipes
    return [RecipeResponse(**recipe.model_dump()) for recipe in all_recipes]

@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe_by_id(recipe_id: int, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get a specific recipe by ID."""
    recipe = repository.get_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump())

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Create a new recipe."""
    recipe = repository.create(recipe_request)
    return RecipeResponse(**recipe.model_dump())

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Update an existing recipe."""
    recipe = repository.update(recipe_id, recipe_request)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump()) 