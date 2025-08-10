"""SQLite implementation of recipe repository."""

import sqlite3
import json
from typing import List, Optional

from app.models import Recipe, RecipeRequest
from .base import RecipeRepository


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
