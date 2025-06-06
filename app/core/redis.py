from redis.asyncio import Redis

redis_client: Redis | None = None


async def init_redis():
    global redis_client
    redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def close_redis():
    if redis_client:
        await redis_client.close()
