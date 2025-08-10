"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    """Health check endpoint to verify the service is running."""
    # Hot reloading test - this change should be picked up automatically
    return "pong"
