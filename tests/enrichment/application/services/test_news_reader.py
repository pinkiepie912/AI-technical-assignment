from datetime import date
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from enrichment.application.exceptions.embedding_exception import EmbeddingError
from enrichment.application.ports.news_search_service_port import (
    NewsSearchParam,
    NewsSearchQuery,
)
from enrichment.application.services.news_reader import NewsReader
from enrichment.domain.entities.new_chunk import NewsChunk
from enrichment.domain.specs.news_serch_spec import NewsSearchContext
from enrichment.infrastructure.exceptions.repository_exception import RepositoryError


@pytest.fixture
def mock_embedding_client():
    return AsyncMock()


@pytest.fixture
def mock_news_repository():
    return AsyncMock()


@pytest.fixture
def news_reader(mock_embedding_client, mock_news_repository):
    return NewsReader(
        embedding_client=mock_embedding_client, news_repository=mock_news_repository
    )


@pytest.mark.asyncio
async def test_get_vectorized_search_query_success(news_reader, mock_embedding_client):
    # Arrange
    queries = [
        NewsSearchQuery(
            query_text="query1",
            company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
        ),
        NewsSearchQuery(
            query_text="query2",
            company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"),
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 28),
        ),
    ]
    mock_embedding_client.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]

    # Act
    result = await news_reader._get_vectorized_search_query(queries)

    # Assert
    mock_embedding_client.generate_embeddings.assert_called_once_with(
        ["query1", "query2"]
    )
    assert len(result) == 2
    assert result[0].company_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14")
    assert result[0].query_vector == [0.1, 0.2]
    assert result[0].start_date == date(2023, 1, 1)
    assert result[0].end_date == date(2023, 1, 31)
    assert result[1].company_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15")
    assert result[1].query_vector == [0.3, 0.4]
    assert result[1].start_date == date(2023, 2, 1)
    assert result[1].end_date == date(2023, 2, 28)


@pytest.mark.asyncio
async def test_get_vectorized_search_query_empty_queries(
    news_reader, mock_embedding_client
):
    # Arrange
    queries = []
    mock_embedding_client.generate_embeddings.return_value = []

    # Act
    result = await news_reader._get_vectorized_search_query(queries)

    # Assert
    mock_embedding_client.generate_embeddings.assert_called_once_with([])
    assert len(result) == 0


@pytest.mark.asyncio
async def test_search_success(news_reader, mock_embedding_client, mock_news_repository):
    # Arrange
    param = NewsSearchParam(
        queries=[
            NewsSearchQuery(
                query_text="query1",
                company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
            ),
            NewsSearchQuery(
                query_text="query2",
                company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"),
                start_date=date(2023, 2, 1),
                end_date=date(2023, 2, 28),
            ),
        ],
        limit_per_query=5,
        similarity_threshold=0.8,
    )
    mock_embedding_client.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]

    mock_news_chunk_1 = NewsChunk(
        id="news1",
        company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
        title="News 1",
        contents="Content 1",
        similarity=0.9,
        # url="http://news1.com",
        # published_date=date(2023, 1, 1),
        # embedding=[0.5, 0.6]
    )
    mock_news_chunk_2 = NewsChunk(
        id="news2",
        company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"),
        title="News 2",
        contents="Content 2",
        similarity=0.9,
        # url="http://news2.com",
        # published_date=date(2023, 2, 1),
        # embedding=[0.7, 0.8]
    )
    mock_news_repository.search.return_value = {
        UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"): [mock_news_chunk_1],
        UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15"): [mock_news_chunk_2],
    }

    # Act
    result = await news_reader.search(param)

    # Assert
    mock_embedding_client.generate_embeddings.assert_called_once()
    mock_news_repository.search.assert_called_once()
    assert len(result) == 2
    assert result[0].company_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14")
    assert result[0].news_chunks[0].title == "News 1"
    assert result[1].company_id == UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15")
    assert result[1].news_chunks[0].title == "News 2"


@pytest.mark.asyncio
async def test_search_no_results(
    news_reader, mock_embedding_client, mock_news_repository
):
    # Arrange
    param = NewsSearchParam(
        queries=[
            NewsSearchQuery(
                query_text="query1",
                company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
            ),
        ],
        limit_per_query=5,
        similarity_threshold=0.8,
    )
    mock_embedding_client.generate_embeddings.return_value = [[0.1, 0.2]]
    mock_news_repository.search.return_value = {}

    # Act
    result = await news_reader.search(param)

    # Assert
    mock_embedding_client.generate_embeddings.assert_called_once()
    mock_news_repository.search.assert_called_once()
    assert len(result) == 0


@pytest.mark.asyncio
async def test_search_empty_params(
    news_reader, mock_embedding_client, mock_news_repository
):
    # Arrange
    param = NewsSearchParam(queries=[], limit_per_query=5, similarity_threshold=0.8)
    mock_embedding_client.generate_embeddings.return_value = []
    mock_news_repository.search.return_value = {}

    # Act
    result = await news_reader.search(param)

    # Assert
    mock_embedding_client.generate_embeddings.assert_called_once_with([])
    mock_news_repository.search.assert_called_once_with(
        NewsSearchContext(queries=[], limit_per_query=5, similarity_threshold=0.8)
    )
    assert len(result) == 0


@pytest.mark.asyncio
async def test_search_embedding_exception(
    news_reader, mock_embedding_client, mock_news_repository
):
    # Arrange
    param = NewsSearchParam(
        queries=[
            NewsSearchQuery(
                query_text="query1",
                company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
            ),
        ],
        limit_per_query=5,
        similarity_threshold=0.8,
    )
    mock_embedding_client.generate_embeddings.side_effect = EmbeddingError(
        "Embedding error"
    )

    # Act & Assert
    with pytest.raises(EmbeddingError):
        await news_reader.search(param)

    mock_embedding_client.generate_embeddings.assert_called_once()
    mock_news_repository.search.assert_not_called()


@pytest.mark.asyncio
async def test_search_repository_exception(
    news_reader, mock_embedding_client, mock_news_repository
):
    # Arrange
    param = NewsSearchParam(
        queries=[
            NewsSearchQuery(
                query_text="query1",
                company_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14"),
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
            ),
        ],
        limit_per_query=5,
        similarity_threshold=0.8,
    )
    mock_embedding_client.generate_embeddings.return_value = [[0.1, 0.2]]
    mock_news_repository.search.side_effect = RepositoryError("Repository error")

    # Act & Assert
    with pytest.raises(RepositoryError):
        await news_reader.search(param)

    mock_embedding_client.generate_embeddings.assert_called_once()
    mock_news_repository.search.assert_called_once()

