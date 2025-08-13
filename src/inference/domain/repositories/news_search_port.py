from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from inference.domain.entities.news_chunk import NewsChunk


class NewsSearchQuery(BaseModel):
    company_id: UUID
    query_text: str
    start_date: date
    end_date: Optional[date] = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class NewsSearchRequest(BaseModel):
    queries: List[NewsSearchQuery]
    limit_per_query: int = Field(default=10)
    similarity_threshold: float = Field(default=0.7)

    model_config = ConfigDict(frozen=True, extra="ignore")


class NewsChunkByCompany(BaseModel):
    company_id: UUID
    news_chunks: List[NewsChunk]

    model_config = ConfigDict(frozen=True, extra="ignore")


class NewsSearchPort(ABC):
    @abstractmethod
    async def search(
        self, param: NewsSearchRequest
    ) -> Dict[UUID, NewsChunkByCompany]: ...
