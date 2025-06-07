import redis.asyncio as redis

redis_client = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            decode_responses=True,
        )
    return redis_client
