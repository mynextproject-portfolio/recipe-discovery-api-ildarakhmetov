"""Recipe management endpoints."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models import RecipeRequest, RecipeResponse, CacheInfo
from app.repositories.base import RecipeRepository
from app.dependencies import get_recipe_repository, get_mealdb_service
from app.services.mealdb import MealDBService

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=List[RecipeResponse])
def get_all_recipes(repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get all available recipes."""
    recipes = repository.get_all()
    return [RecipeResponse(**recipe.model_dump()) for recipe in recipes]


class SearchResultsResponse(BaseModel):
    """Response model for search results with aggregate cache info."""
    recipes: List[RecipeResponse]
    mealdb_cache_info: Optional[CacheInfo] = None

@router.get("/search", response_model=SearchResultsResponse)
async def search_recipes(
    q: Optional[str] = None, 
    repository: RecipeRepository = Depends(get_recipe_repository),
    mealdb_service: MealDBService = Depends(get_mealdb_service)
):
    """Search recipes by title using substring matching (case-insensitive) from both internal database and MealDB API."""
    if not q:
        return SearchResultsResponse(recipes=[])
    
    # Search both internal recipes and MealDB simultaneously
    internal_recipes_task = asyncio.create_task(asyncio.to_thread(repository.search_by_title, q))
    mealdb_recipes_task = asyncio.create_task(mealdb_service.search_meals(q))
    
    # Wait for both searches to complete
    internal_recipes, (mealdb_recipes, mealdb_cache_info) = await asyncio.gather(internal_recipes_task, mealdb_recipes_task)
    
    # Combine results without cache info on individual recipes (since search is cached as a whole)
    all_recipes = []
    
    # Add internal recipes (no cache info since they're from database)
    for recipe in internal_recipes:
        all_recipes.append(RecipeResponse(**recipe.model_dump()))
    
    # Add MealDB recipes without individual cache info
    for recipe in mealdb_recipes:
        all_recipes.append(RecipeResponse(**recipe.model_dump()))
    
    return SearchResultsResponse(recipes=all_recipes, mealdb_cache_info=mealdb_cache_info)


@router.get("/internal/{recipe_id}", response_model=RecipeResponse)
def get_internal_recipe_by_id(recipe_id: int, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Get a specific internal recipe by ID."""
    recipe = repository.get_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Internal recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump())


@router.get("/external/mealdb/{recipe_id}", response_model=RecipeResponse)
async def get_mealdb_recipe_by_id(recipe_id: int, mealdb_service: MealDBService = Depends(get_mealdb_service)):
    """Get a specific MealDB recipe by ID."""
    recipe, cache_info = await mealdb_service.get_meal_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"MealDB recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump(), cache_info=cache_info)


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Create a new recipe."""
    recipe = repository.create(recipe_request)
    return RecipeResponse(**recipe.model_dump())


@router.put("/internal/{recipe_id}", response_model=RecipeResponse)
def update_internal_recipe(recipe_id: int, recipe_request: RecipeRequest, repository: RecipeRepository = Depends(get_recipe_repository)):
    """Update an existing internal recipe. External recipes cannot be updated."""
    recipe = repository.update(recipe_id, recipe_request)
    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Internal recipe with id {recipe_id} not found")
    return RecipeResponse(**recipe.model_dump())
