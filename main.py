from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)

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
        recipe = Recipe(**recipe_request.dict(), id=self._next_id)
        self._recipes.append(recipe)
        self._next_id += 1
        return recipe
    
    def update(self, recipe_id: int, recipe_request: RecipeRequest) -> Optional[Recipe]:
        """Update an existing recipe."""
        for i, recipe in enumerate(self._recipes):
            if recipe.id == recipe_id:
                updated_recipe = Recipe(**recipe_request.dict(), id=recipe_id)
                self._recipes[i] = updated_recipe
                return updated_recipe
        return None

# Singleton repository instance
_repository_instance: Optional[RecipeRepository] = None

# Dependency Injection
def get_recipe_repository() -> RecipeRepository:
    """Dependency injection function for recipe repository."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = InMemoryRecipeRepository()
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
    return [RecipeResponse(**recipe.dict()) for recipe in recipes]

@app.get("/recipes/search", response_model=List[RecipeResponse])
def search_recipes(q: Optional[str] = None, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Search recipes by title using substring matching (case-insensitive)."""
    recipes = repository.search_by_title(q or "")
    return [RecipeResponse(**recipe.dict()) for recipe in recipes]

@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe_by_id(recipe_id: int, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get a specific recipe by ID."""
    recipe = repository.get_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.dict())

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Create a new recipe."""
    recipe = repository.create(recipe_request)
    return RecipeResponse(**recipe.dict())

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Update an existing recipe."""
    recipe = repository.update(recipe_id, recipe_request)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.dict()) 