from fastapi import Depends, FastAPI

from app.core.redis import close_redis, init_redis, redis_client
from app.repository.cache_repository import CacheRepository
from app.services.cashe_service import CacheService

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_redis()


@app.on_event("shutdown")
async def shutdown():
    await close_redis()


# Dependency injection
def get_cache_service() -> CacheService:
    repository = CacheRepository(redis_client)
    return CacheService(repository)


@app.get("/cache/{key}")
async def get_cache(key: str, service: CacheService = Depends(get_cache_service)):
    value = await service.get_cached_data(key)
    return {"key": key, "value": value}


@app.post("/cache/{key}")
async def set_cache(
    key: str, value: str, service: CacheService = Depends(get_cache_service)
):
    await service.cache_data(key, value)
    return {"status": "cached"}
