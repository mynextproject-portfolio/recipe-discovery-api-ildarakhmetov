"""Recipe data models using Pydantic."""

from pydantic import BaseModel
from typing import List, Optional


class CacheInfo(BaseModel):
    """Cache performance information."""
    hit: bool                    # True if cache hit, False if cache miss
    response_time_ms: float     # Response time in milliseconds
    source: str                 # "cache" or "api"


class Recipe(BaseModel):
    """Complete recipe model with all fields."""
    id: Optional[int] = None
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str
    source: str = "internal"  # Default to internal for existing recipes


class RecipeRequest(BaseModel):
    """Request model for creating/updating recipes (without ID)."""
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str


class RecipeResponse(BaseModel):
    """Response model (Recipe with ID)."""
    id: int
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str
    source: str
    cache_info: Optional[CacheInfo] = None
