from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True)
class SearchQuery:
    """기업별 뉴스 검색 쿼리"""

    company_id: UUID
    query_vector: List[float]
    start_date: date
    end_date: Optional[date] = None

    def to_tuple(self):
        """필드 이름과 값을 튜플로 반환"""
        return (self.company_id, self.query_vector, self.start_date, self.end_date)


@dataclass(frozen=True)
class NewsSearchContext:
    queries: List[SearchQuery]
    limit_per_query: int = 10
    similarity_threshold: float = 0.7
