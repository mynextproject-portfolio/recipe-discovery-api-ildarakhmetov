from fastapi import FastAPI

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)


@app.get("/ping")
def ping():
    """Health check endpoint to verify the service is running."""
    return "pong" 