"""Health check endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.cache import RedisCache

router = APIRouter()


@router.get("/ping")
def ping():
    """Simple liveness probe."""
    return "pong"


@router.get("/health")
def health():
    """Comprehensive health check returning overall status and Redis status.

    Returns 200 when all dependencies are healthy, otherwise 503.
    """
    cache = RedisCache()

    try:
        client = cache._get_client()
        redis_ok = client is not None
    except Exception:
        redis_ok = False

    overall_ok = redis_ok

    status_code = 200 if overall_ok else 503
    payload = {
        "status": "ok" if overall_ok else "degraded",
        "redis": "ok" if redis_ok else "unavailable",
    }

    return JSONResponse(status_code=status_code, content=payload)
