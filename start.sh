#!/bin/bash
# Render startup script for Recipe Discovery API

echo "Starting Recipe Discovery API..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "Redis URL configured: ${REDIS_URL:+Yes}"

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
