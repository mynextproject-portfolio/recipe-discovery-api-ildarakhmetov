# Recipe Discovery API - Render Deployment Guide

This guide walks you through deploying the Recipe Discovery API on Render with separate backend and frontend services, using Upstash Redis.

## Architecture

- **Backend**: FastAPI application deployed as a Render Web Service
- **Frontend**: SvelteKit application deployed as a separate Render Web Service  
- **Database**: Upstash Redis (free tier)

## Prerequisites

1. [Render account](https://render.com)
2. [Upstash account](https://upstash.com) with Redis database created
3. This repository pushed to GitHub

## Deployment Options

### Option 1: Deploy from render.yaml (Recommended)

The repository includes a `render.yaml` file that defines both services. This is the easiest method:

1. In Render dashboard, click "New" → "Blueprint"
2. Connect your GitHub repository
3. Select the `render.yaml` file
4. Both services will be created automatically
5. Set the required environment variables (see below)

### Option 2: Manual Service Creation

If you prefer to create services manually:

#### Backend Service

1. In Render dashboard, click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `recipe-discovery-api` (or your preference)
   - **Region**: Oregon (recommended for free tier)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Frontend Service

1. In Render dashboard, click "New" → "Web Service"
2. Connect your GitHub repository  
3. Configure the service:
   - **Name**: `recipe-discovery-frontend` (or your preference)
   - **Region**: Oregon
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: Node
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `node build`

## Environment Variables

After deployment (regardless of method), set these environment variables in the Render dashboard:

### Backend Service Variables

**Required:**
```
REDIS_URL=<your-upstash-redis-url>
ALLOWED_ORIGINS=<your-frontend-url>
```

**Optional (with defaults):**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
API_TITLE=Recipe Discovery API
API_DESCRIPTION=A simple FastAPI service for recipe discovery
API_VERSION=1.0.0
```

**Example values:**
```
REDIS_URL=rediss://default:abc123@us1-example-12345.upstash.io:12345
ALLOWED_ORIGINS=https://recipe-discovery-frontend.onrender.com
```

### Frontend Service Variables

**Required:**
```
PUBLIC_API_URL=<your-backend-url>
PUBLIC_BACKEND_URL=<your-backend-url>
NODE_ENV=production
```

**Example values:**
```
PUBLIC_API_URL=https://recipe-discovery-api.onrender.com
PUBLIC_BACKEND_URL=https://recipe-discovery-api.onrender.com
NODE_ENV=production
```

## Upstash Redis Setup

### 1. Create Database

1. Go to [Upstash Console](https://console.upstash.com/)
2. Click "Create Database"
3. Choose a region close to Oregon (for Render)
4. Select the free tier
5. Create the database

### 2. Get Connection URL

1. In your database dashboard, click "Details"
2. Copy the "Redis URL" (starts with `rediss://`)
3. Use this as your `REDIS_URL` environment variable

## Deployment Order

### If using render.yaml (Blueprint):
1. **Deploy Blueprint** - Both services deploy simultaneously
2. **Set environment variables** - Add Redis URL and configure service URLs
3. **Update CORS** - Set `ALLOWED_ORIGINS` to include frontend URL

### If deploying manually:
Deploy in this order to avoid CORS issues:

1. **Backend first** - Deploy and get the backend URL
2. **Update backend CORS** - Set `ALLOWED_ORIGINS` to include frontend URL
3. **Frontend second** - Deploy with backend URL configured

## Verification

After both services are deployed:

1. Check backend health: `https://your-backend.onrender.com/health`
2. Check frontend: `https://your-frontend.onrender.com`
3. Test API calls by searching for recipes

## Free Tier Limitations

- **Render**: Services sleep after 15 minutes of inactivity
- **Upstash**: 10,000 commands/month limit
- Both are sufficient for development and light usage

## Troubleshooting

### Backend Issues
- Check logs in Render dashboard
- Verify `REDIS_URL` is correctly formatted
- Ensure `ALLOWED_ORIGINS` includes frontend URL

### Frontend Issues
- Verify `PUBLIC_API_URL` points to backend
- Check that backend is responding at `/health`
- Ensure CORS is properly configured on backend

### CORS Errors
- Add frontend URL to backend's `ALLOWED_ORIGINS`
- Include both `http://` and `https://` if needed
- Check for trailing slashes in URLs

## Local Development

For local development with these changes:

1. Copy `env.example` to `.env` (backend)
2. Copy `frontend/env.example` to `frontend/.env` 
3. Update URLs as needed
4. Run with `docker-compose up`
