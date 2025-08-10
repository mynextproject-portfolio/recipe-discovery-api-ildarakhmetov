"""In-memory implementation of recipe repository."""

from typing import List, Optional

from app.models import Recipe, RecipeRequest
from .base import RecipeRepository


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
