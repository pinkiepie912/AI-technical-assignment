from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["CachePort"]


class CachePort(ABC):
    """
    캐시 저장소에 대한 포트 인터페이스

    도메인 계층에서 캐시 기능을 추상화하여 인프라스트럭처 세부사항으로부터 분리
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[dict]:
        """
        캐시에서 데이터 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 데이터 또는 None (캐시 미스)
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """
        캐시에 데이터 저장

        Args:
            key: 캐시 키
            value: 저장할 데이터
            ttl: Time To Live (초 단위, 기본 1시간)

        Returns:
            저장 성공 여부
        """
        ...

    @abstractmethod
    async def invalidate(self, key: str) -> None:
        """
        캐시에서 데이터 삭제

        Args:
            key: 캐시 키
        """
        ...
