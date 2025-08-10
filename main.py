"""
Recipe Discovery API

A FastAPI application for recipe discovery with Redis caching and multiple data sources.
"""

from fastapi import FastAPI

from app.routers import health_router, recipes_router

app = FastAPI(
    title="Recipe Discovery API",
    description="A simple FastAPI service for recipe discovery",
    version="1.0.0"
)

# Include routers
app.include_router(health_router)
app.include_router(recipes_router)
