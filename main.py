from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)

# Recipe request model (for POST/PUT requests)
class RecipeRequest(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str

# Recipe response model (includes ID)
class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str

# Original Recipe data model (keeping for backward compatibility)
class Recipe(BaseModel):
    id: int
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str  # "easy", "medium", "hard"
    cuisine: Optional[str] = None

# In-memory storage for new recipe format
new_recipes_data: List[RecipeResponse] = []
next_recipe_id = 1

# In-memory sample data
recipes_data: List[Recipe] = [
    Recipe(
        id=1,
        title="Classic Chocolate Chip Cookies",
        description="Soft and chewy chocolate chip cookies that are perfect for any occasion",
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
        instructions=[
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
        prep_time_minutes=15,
        cook_time_minutes=10,
        servings=24,
        difficulty="easy",
        cuisine="American"
    ),
    Recipe(
        id=2,
        title="Spaghetti Carbonara",
        description="Traditional Italian pasta dish with eggs, cheese, and pancetta",
        ingredients=[
            "400g spaghetti",
            "200g pancetta or guanciale, diced",
            "4 large eggs",
            "100g Pecorino Romano cheese, grated",
            "Black pepper to taste",
            "Salt for pasta water"
        ],
        instructions=[
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
        prep_time_minutes=10,
        cook_time_minutes=15,
        servings=4,
        difficulty="medium",
        cuisine="Italian"
    ),
    Recipe(
        id=3,
        title="Chicken Tikka Masala",
        description="Creamy and flavorful Indian curry with tender chicken pieces",
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
        instructions=[
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
        prep_time_minutes=45,
        cook_time_minutes=30,
        servings=4,
        difficulty="medium",
        cuisine="Indian"
    ),
    Recipe(
        id=4,
        title="Caesar Salad",
        description="Classic Caesar salad with homemade dressing and croutons",
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
        instructions=[
            "Wash and dry romaine lettuce thoroughly",
            "Make dressing by mashing garlic and anchovies",
            "Whisk in mayonnaise, lemon juice, and Worcestershire",
            "Season with black pepper",
            "Toss lettuce with dressing",
            "Top with Parmesan cheese and croutons",
            "Serve immediately"
        ],
        prep_time_minutes=15,
        cook_time_minutes=0,
        servings=4,
        difficulty="easy",
        cuisine="Italian"
    )
]

@app.get("/ping")
def ping():
    """Health check endpoint to verify the service is running."""
    # Hot reloading test - this change should be picked up automatically
    return "pong"

@app.get("/recipes", response_model=List[Recipe])
def get_all_recipes():
    """Get all available recipes."""
    return recipes_data


@app.get("/recipes/search", response_model=List[Recipe])
def search_recipes(q: Optional[str] = None):
    """Search recipes by title using substring matching (case-insensitive)."""
    # Return empty array if no query parameter provided
    if not q:
        return []
    
    # Convert query to lowercase for case-insensitive search
    query_lower = q.lower()
    
    # Find recipes with titles containing the query string
    matching_recipes = [
        recipe for recipe in recipes_data 
        if query_lower in recipe.title.lower()
    ]
    
    return matching_recipes

@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe_by_id(recipe_id: int):
    """Get a specific recipe by ID."""
    for recipe in recipes_data:
        if recipe.id == recipe_id:
            return recipe
    
    raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")

@app.post("/recipes", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_request: RecipeRequest):
    """Create a new recipe."""
    global next_recipe_id
    
    # Create new recipe with assigned ID
    new_recipe = RecipeResponse(
        id=next_recipe_id,
        title=recipe_request.title,
        ingredients=recipe_request.ingredients,
        steps=recipe_request.steps,
        prepTime=recipe_request.prepTime,
        cookTime=recipe_request.cookTime,
        difficulty=recipe_request.difficulty,
        cuisine=recipe_request.cuisine
    )
    
    # Add to storage and increment ID counter
    new_recipes_data.append(new_recipe)
    next_recipe_id += 1
    
    return new_recipe

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_request: RecipeRequest):
    """Update an existing recipe."""
    # Find the recipe to update
    for i, recipe in enumerate(new_recipes_data):
        if recipe.id == recipe_id:
            # Update the recipe
            updated_recipe = RecipeResponse(
                id=recipe_id,
                title=recipe_request.title,
                ingredients=recipe_request.ingredients,
                steps=recipe_request.steps,
                prepTime=recipe_request.prepTime,
                cookTime=recipe_request.cookTime,
                difficulty=recipe_request.difficulty,
                cuisine=recipe_request.cuisine
            )
            
            # Replace in storage
            new_recipes_data[i] = updated_recipe
            return updated_recipe
    
    raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found") 