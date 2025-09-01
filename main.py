"""
Recipe Discovery API

A FastAPI application for recipe discovery with Redis caching and multiple data sources.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health_router, recipes_router

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # SvelteKit dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://frontend:3000",   # Docker container name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(recipes_router)
