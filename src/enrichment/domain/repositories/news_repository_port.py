from abc import ABC, abstractmethod
from typing import Dict, List
from uuid import UUID

from enrichment.domain.entities.new_chunk import NewsChunk
from enrichment.domain.specs.news_serch_spec import NewsSearchContext


class NewsRepositoryPort(ABC):
    @abstractmethod
    async def search(
        self, context: NewsSearchContext
    ) -> Dict[UUID, List[NewsChunk]]: ...
