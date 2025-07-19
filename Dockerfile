# Use the official Python runtime as a parent image
FROM python:3.12-slim as base

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir watchfiles

# Copy all application files
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application with uvicorn in development mode with hot reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage (default)
FROM base as production

# Copy all application files
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 