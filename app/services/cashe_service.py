from repository.cache_repository import CacheRepository


class CacheService:
    def __init__(self, repository: CacheRepository):
        self.repository = repository

    async def get_cached_data(self, key: str) -> str | None:
        return await self.repository.get(key)

    async def cache_data(self, key: str, value: str, expire: int = 3600):
        await self.repository.set(key, value, expire)

    async def invalidate_cache(self, key: str):
        await self.repository.delete(key)
