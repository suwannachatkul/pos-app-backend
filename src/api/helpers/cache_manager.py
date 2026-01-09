from typing import Any

from aiocache import Cache
from pydantic import BaseModel

from config.cache import CACHE_TTL, cache


class CacheManager:
    """Centralized cache management for the application."""

    def __init__(self, cache_instance: Cache = cache):
        self.cache = cache_instance
        self.ttl_config = CACHE_TTL

    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate consistent cache key from arguments.

        Example:
            generate_key("payment_method", "VISA")
            → "payment_method:VISA"

            generate_key("user", user_id=123)
            → "user:user_id=123"
        """
        parts = [prefix]

        # Add positional args
        parts.extend(str(arg) for arg in args)

        # Add keyword args (sorted for consistency)
        if kwargs:
            kw_str = "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            parts.append(kw_str)

        return ":".join(parts)

    async def get(
        self, key: str, schema: BaseModel | None = None
    ) -> BaseModel | Any | None:
        """
        Get value from cache with optional schema validation.

        Args:
            key: Cache key
            schema: Optional Pydantic schema for validation

        Returns:
            Validated schema instance if schema provided, raw value otherwise
        """
        value = await self.cache.get(key)
        if value is not None and schema is not None:
            return schema.model_validate(value)
        return value

    async def set(
        self, key: str, value: Any | BaseModel, ttl: int | None = None
    ) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (raw or Pydantic model)
            ttl: Time to live in seconds
        """
        if ttl is None:
            ttl = CACHE_TTL.get("default")

        # Serialize Pydantic models to dict
        cache_value = value.model_dump() if isinstance(value, BaseModel) else value
        await self.cache.set(key, cache_value, ttl=ttl)

    async def delete(self, key: str) -> None:
        """Delete specific key from cache."""
        await self.cache.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Example:
            await cache_manager.delete_pattern("payment_method:*")
        """
        # Get Redis connection from aiocache
        redis_conn = await self.cache.get_connection()
        keys = await redis_conn.keys(f"{self.cache.namespace}:{pattern}")

        if keys:
            # Remove namespace prefix for deletion
            clean_keys = [
                key.decode() if isinstance(key, bytes) else key for key in keys
            ]
            await self.cache.delete(*clean_keys)
            return len(clean_keys)
        return 0

    async def clear_all(self) -> None:
        """Clear all cache (use carefully!)."""
        await self.cache.clear()

    # TODO: implement decorator for caching easy cache on functions


# Singleton instance
cache_manager = CacheManager()
