"""Redis caching service."""

import redis
import logging
from typing import Optional


class RedisCache:
    """Service for Redis caching operations."""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.redis_url = redis_url
        self._client = None
    
    def _get_client(self):
        """Get Redis client, creating it if it doesn't exist."""
        if self._client is None:
            try:
                self._client = redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                self._client.ping()
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logging.warning(f"Redis connection failed: {e}. Caching will be disabled.")
                self._client = None
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        client = self._get_client()
        if client is None:
            return None
        
        try:
            return client.get(key)
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.warning(f"Redis get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> bool:
        """Set value in cache with TTL (default 24 hours)."""
        client = self._get_client()
        if client is None:
            return False
        
        try:
            return client.setex(key, ttl_seconds, value)
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logging.warning(f"Redis set failed for key {key}: {e}")
            return False
