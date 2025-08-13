from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from uuid import UUID

from inference.domain.entities.news_chunk import NewsChunk


@dataclass(frozen=True)
class NewsSearchQuery:
    company_id: UUID
    query_text: str
    start_date: date
    end_date: Optional[date] = None


@dataclass(frozen=True)
class NewsSearchParam:
    queries: List[NewsSearchQuery]
    limit_per_query: int = 10
    similarity_threshold: float = 0.7


@dataclass(frozen=True)
class NewsByCompany:
    company_id: UUID
    news_chunks: List[NewsChunk]


class NewsSearchPort(ABC):
    @abstractmethod
    def search(self, param: NewsSearchParam) -> NewsByCompany: ...
