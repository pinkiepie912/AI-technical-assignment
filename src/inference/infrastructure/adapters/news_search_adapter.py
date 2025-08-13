from typing import List

from enrichment.application.ports.news_search_service_port import (
    NewsSearchParam,
    NewsSearchServicePort,
)
from inference.domain.repositories.news_search_port import (
    NewsChunkByCompany,
    NewsSearchPort,
    NewsSearchRequest,
)


class NewsSearchAdapter(NewsSearchPort):
    def __init__(self, news_search_service: NewsSearchServicePort):
        self.news_search_service = news_search_service

    async def search(self, param: NewsSearchRequest) -> List[NewsChunkByCompany]:
        res = await self.news_search_service.search(
            NewsSearchParam(**param.model_dump())
        )

        return [NewsChunkByCompany(**news.model_dump()) for news in res]
