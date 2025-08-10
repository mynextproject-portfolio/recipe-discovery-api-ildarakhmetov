"""Abstract base repository interface for recipe data operations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Recipe, RecipeRequest


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
