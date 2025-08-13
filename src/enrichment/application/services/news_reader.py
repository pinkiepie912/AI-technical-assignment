from typing import List

from enrichment.application.ports.news_search_service_port import (
    NewsByCompany,
    NewsSearchParam,
    NewsSearchQuery,
    NewsSearchServicePort,
)
from enrichment.application.ports.text_embedding_client_port import (
    TextEmbeddingClientPort,
)
from enrichment.domain.repositories.news_repository_port import NewsRepositoryPort
from enrichment.domain.specs.news_serch_spec import NewsSearchContext, SearchQuery


class NewsReader(NewsSearchServicePort):
    def __init__(
        self,
        embedding_client: TextEmbeddingClientPort,
        news_repository: NewsRepositoryPort,
    ):
        self.embedding_client = embedding_client
        self.news_repository = news_repository

    async def search(self, param: NewsSearchParam) -> List[NewsByCompany]:
        search_queries = await self._get_vectorized_search_query(quries=param.queries)

        context = NewsSearchContext(
            queries=search_queries,
            limit_per_query=param.limit_per_query,
            similarity_threshold=param.similarity_threshold,
        )

        news_chunks_map = await self.news_repository.search(context)
        news = []
        for company_id, chunks in news_chunks_map.items():
            news.append(
                NewsByCompany(
                    company_id=company_id,
                    news_chunks=chunks,
                )
            )

        return news

    async def _get_vectorized_search_query(
        self, quries: List[NewsSearchQuery]
    ) -> List[SearchQuery]:
        query_texts = [q.query_text for q in quries]

        vector_list = await self.embedding_client.generate_embeddings(query_texts)

        search_queries = []
        for q, vector in zip(quries, vector_list):
            search_queries.append(
                SearchQuery(
                    company_id=q.company_id,
                    query_vector=vector,
                    start_date=q.start_date,
                    end_date=q.end_date,
                )
            )

        return search_queries
