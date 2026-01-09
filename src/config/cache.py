from aiocache import Cache
from aiocache.serializers import JsonSerializer

from .settings import settings


# Configure Redis cache
cache = Cache(
    Cache.REDIS,
    endpoint=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    timeout=1,
    serializer=JsonSerializer(),
    namespace="payment_app",  # Prefix for all keys
)

# Cache TTL configuration
# TODO use settings from environment
CACHE_TTL = {
    "default": settings.CACHE_DEFAULT_TTL,
    "payment_method": settings.PAYMENT_METHOD_CACHE_TTL,
    "payment_methods_all": settings.CACHE_DEFAULT_TTL,
}
