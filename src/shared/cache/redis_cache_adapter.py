import json
from typing import Optional

from redis.client import Redis

from shared.cache.cache_port import CachePort

__all__ = ["RedisCacheAdapter"]


class RedisCacheAdapter(CachePort):
    """
    Redis 캐시 어댑터
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[dict]:
        """
        캐시 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 데이터 또는 None
        """
        cached_value = await self.redis_client.get(key)

        if cached_value is None:
            return None

        result = json.loads(cached_value)
        return result

    async def set(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """
        캐시 데이터 저장

        Args:
            key: 캐시 키
            value: 저장할 데이터
            ttl: Time To Live (초 단위, 기본 1시간)

        Returns:
            저장 성공 여부
        """

        serialized_value = json.dumps(value, ensure_ascii=False)
        result = await self.redis_client.setex(key, ttl, serialized_value)
        return bool(result)

    async def invalidate(self, key: str) -> None:
        """
        캐시 데이터 삭제

        Args:
            key: 캐시 키

        """

        await self.redis_client.delete(key)
