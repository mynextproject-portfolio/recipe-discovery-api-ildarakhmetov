"""MealDB API service for recipe discovery."""

import httpx
import json
import logging
import time
from json import JSONDecodeError
from typing import List, Optional, Tuple

from app.models import Recipe, CacheInfo
from .cache import RedisCache


class MealDBService:
    """Service for interacting with TheMealDB API with Redis caching."""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    CACHE_TTL = 86400  # 24 hours in seconds
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    async def get_meal_by_id(self, meal_id: int) -> Tuple[Optional[Recipe], CacheInfo]:
        """Get a specific meal by ID from TheMealDB API with Redis caching."""
        start_time = time.time()
        
        # Create cache key for individual meal
        cache_key = f"mealdb:meal:{meal_id}"
        
        # Try to get from cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            try:
                # Deserialize cached recipe
                cached_data = json.loads(cached_result)
                response_time_ms = (time.time() - start_time) * 1000
                cache_info = CacheInfo(hit=True, response_time_ms=response_time_ms, source="cache")
                
                if cached_data:  # Check if not None/empty
                    return Recipe(**cached_data), cache_info
                else:
                    return None, cache_info  # Cached "not found" result
            except (JSONDecodeError, TypeError) as e:
                logging.warning(f"Failed to deserialize cached meal {meal_id}: {e}")
                # Continue to fetch from API if cache is corrupted
        
        # Cache miss - fetch from MealDB API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.BASE_URL}/lookup.php", params={"i": meal_id})
                response.raise_for_status()
                data = response.json()
                
                response_time_ms = (time.time() - start_time) * 1000
                cache_info = CacheInfo(hit=False, response_time_ms=response_time_ms, source="api")
                
                if not data.get("meals") or not data["meals"]:
                    # Cache negative result to avoid repeated API calls
                    await self.cache.set(cache_key, json.dumps(None), self.CACHE_TTL)
                    return None, cache_info
                
                meal = data["meals"][0]  # MealDB returns array with single item
                recipe = self._transform_meal_to_recipe(meal)
                
                # Cache the result
                try:
                    await self.cache.set(cache_key, json.dumps(recipe.model_dump()), self.CACHE_TTL)
                except (TypeError, Exception) as e:
                    logging.warning(f"Failed to cache meal {meal_id}: {e}")
                
                return recipe, cache_info
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            logging.error(f"Error fetching meal {meal_id} from MealDB: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            cache_info = CacheInfo(hit=False, response_time_ms=response_time_ms, source="api")
            # Cache negative result to avoid repeated failures
            await self.cache.set(cache_key, json.dumps(None), 300)  # 5 minute cache for errors
            return None, cache_info

    async def search_meals(self, query: str) -> Tuple[List[Recipe], CacheInfo]:
        """Search for meals by name from TheMealDB API with Redis caching."""
        start_time = time.time()
        
        if not query:
            response_time_ms = (time.time() - start_time) * 1000
            cache_info = CacheInfo(hit=False, response_time_ms=response_time_ms, source="cache")
            return [], cache_info
        
        # Create cache key including the search query
        cache_key = f"mealdb:search:{query.lower().strip()}"
        
        # Try to get from cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            try:
                # Deserialize cached recipes
                cached_data = json.loads(cached_result)
                response_time_ms = (time.time() - start_time) * 1000
                cache_info = CacheInfo(hit=True, response_time_ms=response_time_ms, source="cache")
                
                recipes = []
                for recipe_data in cached_data:
                    recipe = Recipe(**recipe_data)
                    recipes.append(recipe)
                return recipes, cache_info
            except (JSONDecodeError, TypeError) as e:
                logging.warning(f"Failed to deserialize cached data for key {cache_key}: {e}")
                # Continue to fetch from API if cache is corrupted
        
        # Cache miss - fetch from MealDB API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.BASE_URL}/search.php", params={"s": query})
                response.raise_for_status()
                data = response.json()
                
                response_time_ms = (time.time() - start_time) * 1000
                cache_info = CacheInfo(hit=False, response_time_ms=response_time_ms, source="api")
                
                if not data.get("meals"):
                    # Cache empty results too to avoid repeated API calls for non-existent recipes
                    await self.cache.set(cache_key, json.dumps([]), self.CACHE_TTL)
                    return [], cache_info
                
                recipes = []
                for meal in data["meals"]:
                    recipe = self._transform_meal_to_recipe(meal)
                    recipes.append(recipe)
                
                # Cache the results
                try:
                    recipes_data = [recipe.model_dump() for recipe in recipes]
                    await self.cache.set(cache_key, json.dumps(recipes_data), self.CACHE_TTL)
                except (TypeError, Exception) as e:
                    logging.warning(f"Failed to cache recipes for key {cache_key}: {e}")
                
                return recipes, cache_info
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            # Log error in production, for now return empty list to not break search
            logging.error(f"Error fetching from MealDB: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            cache_info = CacheInfo(hit=False, response_time_ms=response_time_ms, source="api")
            return [], cache_info
    
    def _transform_meal_to_recipe(self, meal: dict) -> Recipe:
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
