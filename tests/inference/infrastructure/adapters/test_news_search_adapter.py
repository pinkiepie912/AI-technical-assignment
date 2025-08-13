import pytest
from unittest.mock import AsyncMock
from uuid import UUID
from datetime import date

from enrichment.application.ports.news_search_service_port import NewsSearchParam, NewsByCompany as EnrichmentNewsByCompany, NewsChunk as EnrichmentNewsChunk
from inference.domain.repositories.news_search_port import NewsSearchRequest, NewsChunkByCompany, NewsChunk
from inference.infrastructure.adapters.news_search_adapter import NewsSearchAdapter


class TestNewsSearchAdapter:
    @pytest.fixture
    def mock_news_search_service(self):
        return AsyncMock()

    @pytest.fixture
    def adapter(self, mock_news_search_service):
        return NewsSearchAdapter(news_search_service=mock_news_search_service)

    @pytest.mark.asyncio
    async def test_search_success(self, adapter, mock_news_search_service):
        # Arrange
        company_id_1 = UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14')
        company_id_2 = UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15')

        request_param = NewsSearchRequest(
            queries=[
                {"query_text": "query1", "company_id": str(company_id_1), "start_date": "2023-01-01", "end_date": "2023-01-31"},
                {"query_text": "query2", "company_id": str(company_id_2), "start_date": "2023-02-01", "end_date": "2023-02-28"},
            ],
            limit_per_query=5,
            similarity_threshold=0.8
        )

        mock_enrichment_news_chunks_1 = [
            EnrichmentNewsChunk(id=1, company_id=company_id_1, title="News 1", contents="Content 1", similarity=0.9)
        ]
        mock_enrichment_news_chunks_2 = [
            EnrichmentNewsChunk(id=2, company_id=company_id_2, title="News 2", contents="Content 2", similarity=0.85)
        ]

        mock_news_search_service.search.return_value = [
            EnrichmentNewsByCompany(company_id=company_id_1, news_chunks=mock_enrichment_news_chunks_1),
            EnrichmentNewsByCompany(company_id=company_id_2, news_chunks=mock_enrichment_news_chunks_2)
        ]

        # Act
        result = await adapter.search(request_param)

        # Assert
        mock_news_search_service.search.assert_called_once()
        assert len(result) == 2

        assert result[0].company_id == company_id_1
        assert len(result[0].news_chunks) == 1
        assert result[0].news_chunks[0].id == 1
        assert result[0].news_chunks[0].title == "News 1"
        assert result[0].news_chunks[0].contents == "Content 1"

        assert result[1].company_id == company_id_2
        assert len(result[1].news_chunks) == 1
        assert result[1].news_chunks[0].id == 2
        assert result[1].news_chunks[0].title == "News 2"
        assert result[1].news_chunks[0].contents == "Content 2"
        

    @pytest.mark.asyncio
    async def test_search_no_results(self, adapter, mock_news_search_service):
        # Arrange
        company_id = UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14')
        request_param = NewsSearchRequest(
            queries=[
                {"query_text": "query1", "company_id": str(company_id), "start_date": "2023-01-01", "end_date": "2023-01-31"},
            ],
            limit_per_query=5,
            similarity_threshold=0.8
        )
        mock_news_search_service.search.return_value = []

        # Act
        result = await adapter.search(request_param)

        # Assert
        mock_news_search_service.search.assert_called_once()
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_empty_queries_in_request(self, adapter, mock_news_search_service):
        # Arrange
        request_param = NewsSearchRequest(
            queries=[],
            limit_per_query=5,
            similarity_threshold=0.8
        )
        mock_news_search_service.search.return_value = []

        # Act
        result = await adapter.search(request_param)

        # Assert
        mock_news_search_service.search.assert_called_once()
        assert len(result) == 0
