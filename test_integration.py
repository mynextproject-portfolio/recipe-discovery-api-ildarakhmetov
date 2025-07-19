import pytest
from fastapi.testclient import TestClient
from main import app, get_recipe_repository, RecipeRepository, InMemoryRecipeRepository

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_data():
    """Reset the repository data before each test to ensure clean state."""
    # Get a fresh repository instance for testing
    repository = get_recipe_repository()
    
    # Since we're using a singleton, we need to reset its internal state
    if isinstance(repository, InMemoryRecipeRepository):
        # Reset to only sample data (first 4 recipes) and set next ID to 5
        repository._recipes = repository._recipes[:4]  # Keep only the 4 sample recipes
        repository._next_id = 5  # Start at 5 to avoid overlap with sample data (IDs 1-4)
    
    yield repository
    
    # The singleton will maintain state, which is what we want for the application


class TestHealthCheck:
    """Test the health check endpoint."""
    
    def test_ping_endpoint(self):
        """Test GET /ping returns correct response."""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == "pong"


class TestGetRecipes:
    """Test the get all recipes endpoint."""
    
    def test_get_all_recipes(self):
        """Test GET /recipes returns all sample recipes."""
        response = client.get("/recipes")
        assert response.status_code == 200
        
        recipes = response.json()
        assert len(recipes) >= 4  # We have at least 4 sample recipes
        
        # Verify first recipe structure
        first_recipe = recipes[0]
        assert first_recipe["id"] == 1
        assert first_recipe["title"] == "Classic Chocolate Chip Cookies"
        assert "ingredients" in first_recipe
        assert "steps" in first_recipe
        assert "prepTime" in first_recipe
        assert "cookTime" in first_recipe
        assert "difficulty" in first_recipe
        assert "cuisine" in first_recipe


class TestGetRecipeById:
    """Test the get recipe by ID endpoint."""
    
    def test_get_existing_recipe(self):
        """Test GET /recipes/{id} for existing recipe."""
        response = client.get("/recipes/1")
        assert response.status_code == 200
        
        recipe = response.json()
        assert recipe["id"] == 1
        assert recipe["title"] == "Classic Chocolate Chip Cookies"
        assert recipe["difficulty"] == "easy"
        assert recipe["cuisine"] == "American"
    
    def test_get_nonexistent_recipe(self):
        """Test GET /recipes/{id} for non-existent recipe returns 404."""
        response = client.get("/recipes/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestSearchRecipes:
    """Test the search recipes endpoint."""
    
    def test_search_with_query(self):
        """Test GET /recipes/search with a query parameter."""
        response = client.get("/recipes/search?q=chocolate")
        assert response.status_code == 200
        
        recipes = response.json()
        assert len(recipes) == 1
        assert recipes[0]["title"] == "Classic Chocolate Chip Cookies"
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        response = client.get("/recipes/search?q=CHOCOLATE")
        assert response.status_code == 200
        
        recipes = response.json()
        assert len(recipes) == 1
        assert recipes[0]["title"] == "Classic Chocolate Chip Cookies"
    
    def test_search_partial_match(self):
        """Test search works with partial matches."""
        response = client.get("/recipes/search?q=pasta")
        assert response.status_code == 200
        
        recipes = response.json()
        # Should find recipes containing "pasta" in title - none in our sample data
        assert len(recipes) == 0
    
    def test_search_italian_cuisine(self):
        """Test search for Italian recipes."""
        response = client.get("/recipes/search?q=Caesar")
        assert response.status_code == 200
        
        recipes = response.json()
        assert len(recipes) == 1
        assert recipes[0]["title"] == "Caesar Salad"
    
    def test_search_no_query_parameter(self):
        """Test search without query parameter returns empty array."""
        response = client.get("/recipes/search")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_search_empty_query(self):
        """Test search with empty query returns empty array."""
        response = client.get("/recipes/search?q=")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_search_no_matches(self):
        """Test search with query that has no matches."""
        response = client.get("/recipes/search?q=nonexistentrecipe")
        assert response.status_code == 200
        assert response.json() == []


class TestCreateRecipe:
    """Test the create recipe endpoint."""
    
    def test_create_recipe_success(self, reset_data):
        """Test POST /recipes creates a new recipe successfully."""
        new_recipe_data = {
            "title": "Test Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "steps": ["step 1", "step 2"],
            "prepTime": "10 minutes",
            "cookTime": "20 minutes",
            "difficulty": "easy",
            "cuisine": "Test Cuisine"
        }
        
        response = client.post("/recipes", json=new_recipe_data)
        assert response.status_code == 201
        
        created_recipe = response.json()
        assert created_recipe["id"] >= 5  # Should get next available ID
        assert created_recipe["title"] == "Test Recipe"
        assert created_recipe["ingredients"] == ["ingredient 1", "ingredient 2"]
        assert created_recipe["steps"] == ["step 1", "step 2"]
        assert created_recipe["prepTime"] == "10 minutes"
        assert created_recipe["cookTime"] == "20 minutes"
        assert created_recipe["difficulty"] == "easy"
        assert created_recipe["cuisine"] == "Test Cuisine"
    
    def test_create_recipe_increments_id(self, reset_data):
        """Test that creating multiple recipes increments the ID."""
        recipe_data = {
            "title": "Recipe 1",
            "ingredients": ["ingredient"],
            "steps": ["step"],
            "prepTime": "5 min",
            "cookTime": "10 min",
            "difficulty": "easy",
            "cuisine": "Test"
        }
        
        # Create first recipe
        response1 = client.post("/recipes", json=recipe_data)
        assert response1.status_code == 201
        first_id = response1.json()["id"]
        
        # Create second recipe
        recipe_data["title"] = "Recipe 2"
        response2 = client.post("/recipes", json=recipe_data)
        assert response2.status_code == 201
        second_id = response2.json()["id"]
        
        # Second ID should be greater than first
        assert second_id > first_id
    
    def test_create_recipe_missing_fields(self):
        """Test POST /recipes with missing required fields."""
        incomplete_recipe = {
            "title": "Incomplete Recipe"
            # Missing required fields
        }
        
        response = client.post("/recipes", json=incomplete_recipe)
        assert response.status_code == 422  # Validation error


class TestUpdateRecipe:
    """Test the update recipe endpoint."""
    
    def test_update_existing_recipe(self, reset_data):
        """Test PUT /recipes/{id} updates an existing recipe."""
        # First create a recipe
        create_data = {
            "title": "Original Recipe",
            "ingredients": ["original ingredient"],
            "steps": ["original step"],
            "prepTime": "5 min",
            "cookTime": "10 min",
            "difficulty": "easy",
            "cuisine": "Original"
        }
        
        create_response = client.post("/recipes", json=create_data)
        assert create_response.status_code == 201
        created_recipe = create_response.json()
        recipe_id = created_recipe["id"]
        
        # Now update the recipe
        update_data = {
            "title": "Updated Recipe",
            "ingredients": ["updated ingredient 1", "updated ingredient 2"],
            "steps": ["updated step 1", "updated step 2"],
            "prepTime": "15 min",
            "cookTime": "25 min",
            "difficulty": "medium",
            "cuisine": "Updated"
        }
        
        update_response = client.put(f"/recipes/{recipe_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_recipe = update_response.json()
        assert updated_recipe["id"] == recipe_id
        assert updated_recipe["title"] == "Updated Recipe"
        assert updated_recipe["ingredients"] == ["updated ingredient 1", "updated ingredient 2"]
        assert updated_recipe["steps"] == ["updated step 1", "updated step 2"]
        assert updated_recipe["prepTime"] == "15 min"
        assert updated_recipe["cookTime"] == "25 min"
        assert updated_recipe["difficulty"] == "medium"
        assert updated_recipe["cuisine"] == "Updated"
    
    def test_update_nonexistent_recipe(self):
        """Test PUT /recipes/{id} for non-existent recipe returns 404."""
        update_data = {
            "title": "Should Fail",
            "ingredients": ["ingredient"],
            "steps": ["step"],
            "prepTime": "5 min",
            "cookTime": "10 min",
            "difficulty": "easy",
            "cuisine": "Test"
        }
        
        response = client.put("/recipes/999", json=update_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestHappyPathCRUDCycle:
    """Test the complete CRUD + search cycle end-to-end."""
    
    def test_complete_crud_and_search_cycle(self, reset_data):
        """Test the complete happy path: create → get → search → update → verify."""
        
        # Step 1: Create a new recipe
        recipe_data = {
            "title": "Happy Path Recipe",
            "ingredients": ["flour", "sugar", "eggs"],
            "steps": ["mix ingredients", "bake for 30 minutes"],
            "prepTime": "15 minutes",
            "cookTime": "30 minutes",
            "difficulty": "medium",
            "cuisine": "Test Cuisine"
        }
        
        create_response = client.post("/recipes", json=recipe_data)
        assert create_response.status_code == 201
        
        created_recipe = create_response.json()
        recipe_id = created_recipe["id"]
        assert created_recipe["title"] == "Happy Path Recipe"
        
        # Step 2: Get recipe by ID to verify it was created
        get_response = client.get(f"/recipes/{recipe_id}")
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == "Happy Path Recipe"
        assert retrieved_recipe["id"] == recipe_id
        
        # Step 3: Search for the created recipe
        search_response = client.get("/recipes/search?q=Happy Path")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        # With dependency injection, newly created recipes are searchable
        assert len(search_results) == 1
        found_recipe = search_results[0]
        assert found_recipe["title"] == "Happy Path Recipe"
        assert found_recipe["id"] == recipe_id
        
        # Step 4: Update the recipe
        updated_recipe_data = {
            "title": "Updated Happy Path Recipe",
            "ingredients": ["flour", "sugar", "eggs", "vanilla"],
            "steps": ["mix ingredients", "add vanilla", "bake for 35 minutes"],
            "prepTime": "20 minutes",
            "cookTime": "35 minutes",
            "difficulty": "easy",
            "cuisine": "Updated Test Cuisine"
        }
        
        update_response = client.put(f"/recipes/{recipe_id}", json=updated_recipe_data)
        assert update_response.status_code == 200
        
        updated_recipe = update_response.json()
        assert updated_recipe["id"] == recipe_id
        assert updated_recipe["title"] == "Updated Happy Path Recipe"
        assert len(updated_recipe["ingredients"]) == 4
        assert "vanilla" in updated_recipe["ingredients"]
        assert updated_recipe["prepTime"] == "20 minutes"
        assert updated_recipe["cookTime"] == "35 minutes"
        assert updated_recipe["difficulty"] == "easy"
        
        # Step 5: Verify the update persisted
        final_get_response = client.get(f"/recipes/{recipe_id}")
        assert final_get_response.status_code == 200
        final_recipe = final_get_response.json()
        assert final_recipe["title"] == "Updated Happy Path Recipe"
        assert final_recipe["difficulty"] == "easy"


class TestDataConsistency:
    """Test to verify data consistency works with dependency injection."""
    
    def test_unified_data_consistency(self, reset_data):
        """Test that demonstrates data consistency works with dependency injection."""
        
        # Create a recipe using POST /recipes
        recipe_data = {
            "title": "Consistency Test Recipe",
            "ingredients": ["test ingredient"],
            "steps": ["test step"],
            "prepTime": "5 min",
            "cookTime": "10 min",
            "difficulty": "easy",
            "cuisine": "Test"
        }
        
        create_response = client.post("/recipes", json=recipe_data)
        assert create_response.status_code == 201
        created_recipe = create_response.json()
        
        # Get recipe by ID should work
        get_response = client.get(f"/recipes/{created_recipe['id']}")
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == "Consistency Test Recipe"
        assert retrieved_recipe["id"] == created_recipe["id"]
        
        # Search should find the recipe
        search_response = client.get("/recipes/search?q=Consistency Test")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 1
        assert search_results[0]["title"] == "Consistency Test Recipe"


if __name__ == "__main__":
    pytest.main([__file__]) 