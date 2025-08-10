"""Dependency injection for FastAPI application."""

from typing import Optional

from app.repositories.base import RecipeRepository
from app.repositories.sqlite import SQLiteRecipeRepository
from app.services.cache import RedisCache
from app.services.mealdb import MealDBService

# Singleton instances
_repository_instance: Optional[RecipeRepository] = None
_cache_instance: Optional[RedisCache] = None
_mealdb_service_instance: Optional[MealDBService] = None


def get_recipe_repository() -> RecipeRepository:
    """Dependency injection function for recipe repository."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = SQLiteRecipeRepository()
    return _repository_instance


def get_cache() -> RedisCache:
    """Get Redis cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def get_mealdb_service() -> MealDBService:
    """Get MealDB service instance."""
    global _mealdb_service_instance
    if _mealdb_service_instance is None:
        cache = get_cache()
        _mealdb_service_instance = MealDBService(cache)
    return _mealdb_service_instance
