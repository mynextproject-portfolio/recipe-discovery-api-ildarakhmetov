# Build a Recipe Discovery API with Architecture Patterns 

Learn to build a production-ready Recipe Discovery API using FastAPI and Python. This project demonstrates the evolution from monolithic code to well-architected services through progressive refactoring. You'll work with client personas to gather requirements, implement basic CRUD functionality, integrate external APIs, add caching with Redis, and refactor to clean, testable architecture patterns.

## Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

3. Access the API documentation at: http://localhost:8000/docs

## Testing

The project includes comprehensive integration tests for all API endpoints.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_integration.py

# Run specific test class
pytest test_integration.py::TestSearchRecipes
```

### Test Coverage

The test suite includes:
- ✅ Health check endpoint (`/ping`)
- ✅ Get all recipes (`/recipes`)
- ✅ Get recipe by ID (`/recipes/{id}`)
- ✅ Search recipes (`/recipes/search`)
- ✅ Create recipe (`POST /recipes`)
- ✅ Update recipe (`PUT /recipes/{id}`)
- ✅ Complete CRUD + search workflow
- ✅ Error handling and edge cases

---

*Part of [mynextproject.dev](https://mynextproject.dev) - Learn to code like a professional*
