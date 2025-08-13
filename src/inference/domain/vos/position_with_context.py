from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from inference.controllers.dtos.talent_infer import Position
from inference.domain.aggregates.company_context import CompanyContext
from inference.domain.entities.news_chunk import NewsChunk

__all__ = ["PositionWithContext"]


@dataclass(frozen=True)
class PositionWithContext:
    """
    Position과 관련된 모든 컨텍스트 정보를 담는 Value Object
    """

    position: Position
    company_context: Optional[CompanyContext]
    related_news: List[NewsChunk]

    def get_chronological_order_key(self) -> tuple:
        """
        시간순 정렬을 위한 키 생성

        Returns:
            tuple: (year, month) 튜플. month가 None인 경우 1로 처리
        """
        start_date = self.position.startEndDate.start
        return (start_date.year, start_date.month or 1)

