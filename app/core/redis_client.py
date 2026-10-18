import redis.asyncio as aioredis

from app.core.config import settings


# Global Redis client (async)
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency — provides Redis client."""
    return redis_client


async def close_redis() -> None:
    """Close Redis connection on shutdown."""
    await redis_client.aclose()