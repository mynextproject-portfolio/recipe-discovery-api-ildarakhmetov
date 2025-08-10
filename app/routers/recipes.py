"""Recipe management endpoints."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.models import RecipeRequest, RecipeResponse
from app.repositories.base import RecipeRepository
from app.dependencies import get_recipe_repository, get_mealdb_service
from app.services.mealdb import MealDBService

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=List[RecipeResponse])
def get_all_recipes(repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get all available recipes."""
    recipes = repository.get_all()
    return [RecipeResponse(**recipe.model_dump()) for recipe in recipes]


@router.get("/search", response_model=List[RecipeResponse])
async def search_recipes(
    q: Optional[str] = None, 
    repository: RecipeRepository = Depends(get_recipe_repository),
    mealdb_service: MealDBService = Depends(get_mealdb_service)
):
    """Search recipes by title using substring matching (case-insensitive) from both internal database and MealDB API."""
    if not q:
        return []
    
    # Search both internal recipes and MealDB simultaneously
    internal_recipes_task = asyncio.create_task(asyncio.to_thread(repository.search_by_title, q))
    mealdb_recipes_task = asyncio.create_task(mealdb_service.search_meals(q))
    
    # Wait for both searches to complete
    internal_recipes, mealdb_recipes = await asyncio.gather(internal_recipes_task, mealdb_recipes_task)
    
    # Combine results
    all_recipes = internal_recipes + mealdb_recipes
    return [RecipeResponse(**recipe.model_dump()) for recipe in all_recipes]


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe_by_id(recipe_id: int, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get a specific recipe by ID."""
    recipe = repository.get_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump())


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Create a new recipe."""
    recipe = repository.create(recipe_request)
    return RecipeResponse(**recipe.model_dump())


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Update an existing recipe."""
    recipe = repository.update(recipe_id, recipe_request)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump())
