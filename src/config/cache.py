from aiocache import Cache
from aiocache.serializers import JsonSerializer

from .settings import settings


# Configure Redis cache
cache = Cache(
    Cache.REDIS,
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    timeout=settings.REDIS_POOL_TIMEOUT,
    serializer=JsonSerializer(),
    namespace="payment_app",  # Prefix for all keys
    pool_max_size=settings.REDIS_POOL_SIZE,
)

# Cache TTL configuration
# TODO move some TTLs to services scope if needed
CACHE_TTL = {
    "default": settings.CACHE_DEFAULT_TTL,
    "payment_method": settings.PAYMENT_METHOD_CACHE_TTL,
    "payment_methods_all": settings.CACHE_DEFAULT_TTL,
}
