import abc


class IDistributedCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> str | None:
        """Gets a value from the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    async def set(self, key: str, value: str) -> None:
        """Sets a value in the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """Deletes a value from the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    async def exists(self, key: str) -> bool:
        """Checks if a key exists in the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(self) -> None:
        """Clears all items from the cache."""
        raise NotImplementedError
