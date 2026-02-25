import redis.asyncio as redis

from app.domain.interfaces import distributed_cache


class RedisCache(distributed_cache.IDistributedCache):
    def __init__(self, host: str, port: int):
        self._client: redis.Redis[str] = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: str) -> None:
        await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def clear(self) -> None:
        await self._client.flushdb()
