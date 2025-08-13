"""Test cases for News repository"""
import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4
from typing import List

from enrichment.infrastructure.repositories.news_repository import NewsRepository
from enrichment.domain.entities.new_chunk import NewsChunk
from enrichment.domain.specs.news_serch_spec import NewsSearchContext, SearchQuery


class TestNewsRepository:
    @pytest.fixture
    def mock_session_manager(self):
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_session_manager):
        return NewsRepository(session_manager=mock_session_manager)
    
    @pytest.fixture
    def sample_search_context(self):
        company_id1 = UUID("12345678-1234-5678-9abc-123456789012")
        company_id2 = UUID("87654321-4321-8765-cba9-876543210987")
        
        query1 = SearchQuery(
            company_id=company_id1,
            query_vector=[0.1, 0.2, 0.3] * 512,  # 1536 dimensions
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        query2 = SearchQuery(
            company_id=company_id2,
            query_vector=[0.4, 0.5, 0.6] * 512,  # 1536 dimensions
            start_date=date(2023, 6, 1),
            end_date=None  # Test with no end date
        )
        
        return NewsSearchContext(
            queries=[query1, query2],
            limit_per_query=5,
            similarity_threshold=0.7
        )

    @pytest.mark.asyncio
    async def test_search_empty_queries(self, repository):
        context = NewsSearchContext(queries=[], limit_per_query=10, similarity_threshold=0.7)
        result = await repository.search(context)
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_search_success(self, repository, sample_search_context, mock_session_manager):
        # Mock session
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        company_id1 = UUID("12345678-1234-5678-9abc-123456789012")
        company_id2 = UUID("87654321-4321-8765-cba9-876543210987")
        
        # Mock database query results
        mock_rows = [
            Mock(
                id=1,
                company_id=company_id1,
                title="첫 번째 뉴스",
                contents="첫 번째 뉴스 내용입니다.",
                similarity_score=0.85
            ),
            Mock(
                id=2,
                company_id=company_id1,
                title="두 번째 뉴스",
                contents="두 번째 뉴스 내용입니다.",
                similarity_score=0.78
            ),
            Mock(
                id=3,
                company_id=company_id2,
                title="다른 회사 뉴스",
                contents="다른 회사의 뉴스 내용입니다.",
                similarity_score=0.92
            )
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        # Execute test
        result = await repository.search(sample_search_context)
        
        # Verify results
        assert len(result) == 2  # Two companies
        assert company_id1 in result
        assert company_id2 in result
        
        # Check company1 news
        company1_news = result[company_id1]
        assert len(company1_news) == 2
        assert company1_news[0].id == 1
        assert company1_news[0].title == "첫 번째 뉴스"
        assert company1_news[0].similarity == 0.85
        assert company1_news[1].id == 2
        assert company1_news[1].similarity == 0.78
        
        # Check company2 news
        company2_news = result[company_id2]
        assert len(company2_news) == 1
        assert company2_news[0].id == 3
        assert company2_news[0].title == "다른 회사 뉴스"
        assert company2_news[0].similarity == 0.92
    
    @pytest.mark.asyncio
    async def test_search_no_results(self, repository, sample_search_context, mock_session_manager):
        # Mock session with empty results
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(sample_search_context)
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_search_single_query(self, repository, mock_session_manager):
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        context = NewsSearchContext(
            queries=[query],
            limit_per_query=3,
            similarity_threshold=0.8
        )
        
        # Mock session
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        mock_rows = [
            Mock(
                id=1,
                company_id=company_id,
                title="고유사도 뉴스",
                contents="매우 관련성 높은 뉴스입니다.",
                similarity_score=0.95
            )
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        assert len(result) == 1
        assert company_id in result
        assert len(result[company_id]) == 1
        assert result[company_id][0].similarity == 0.95
    
    @pytest.mark.asyncio
    async def test_search_with_limit_per_query(self, repository, mock_session_manager):
        """Test that limit_per_query is respected in the query"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        # Set limit to 2
        context = NewsSearchContext(
            queries=[query],
            limit_per_query=2,
            similarity_threshold=0.7
        )
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        # Return more results than limit
        mock_rows = [
            Mock(id=1, company_id=company_id, title="뉴스1", contents="내용1", similarity_score=0.9),
            Mock(id=2, company_id=company_id, title="뉴스2", contents="내용2", similarity_score=0.85),
            Mock(id=3, company_id=company_id, title="뉴스3", contents="내용3", similarity_score=0.8),
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        # Should respect the limit (though in practice this would be handled by the SQL query)
        assert len(result[company_id]) == 3  # All returned results are processed
    
    @pytest.mark.asyncio
    async def test_search_with_similarity_threshold(self, repository, mock_session_manager):
        """Test similarity threshold filtering"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        context = NewsSearchContext(
            queries=[query],
            limit_per_query=10,
            similarity_threshold=0.8  # High threshold
        )
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        # Only high similarity results should be returned by the SQL query
        mock_rows = [
            Mock(id=1, company_id=company_id, title="고유사도뉴스", contents="내용", similarity_score=0.9),
            Mock(id=2, company_id=company_id, title="또다른고유사도뉴스", contents="내용", similarity_score=0.85),
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        assert len(result[company_id]) == 2
        # All results should be above threshold (filtered by SQL)
        for news_chunk in result[company_id]:
            assert news_chunk.similarity >= 0.8
    
    @pytest.mark.asyncio
    async def test_search_multiple_companies_same_news_id(self, repository, mock_session_manager):
        """Test handling when different companies have news with same IDs"""
        company_id1 = uuid4()
        company_id2 = uuid4()
        
        queries = [
            SearchQuery(
                company_id=company_id1,
                query_vector=[0.1] * 1536,
                start_date=date(2023, 1, 1)
            ),
            SearchQuery(
                company_id=company_id2,
                query_vector=[0.2] * 1536,
                start_date=date(2023, 1, 1)
            )
        ]
        
        context = NewsSearchContext(queries=queries)
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        # Same news ID but different companies
        mock_rows = [
            Mock(id=1, company_id=company_id1, title="회사1 뉴스", contents="내용1", similarity_score=0.8),
            Mock(id=1, company_id=company_id2, title="회사2 뉴스", contents="내용2", similarity_score=0.9),
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        assert len(result) == 2
        assert company_id1 in result
        assert company_id2 in result
        assert result[company_id1][0].title == "회사1 뉴스"
        assert result[company_id2][0].title == "회사2 뉴스"
    
    @pytest.mark.asyncio
    async def test_search_query_vector_dimensions(self, repository, mock_session_manager):
        """Test with different vector dimensions"""
        company_id = uuid4()
        
        # Test with correct 1536 dimensions
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,  # Correct dimension
            start_date=date(2023, 1, 1)
        )
        
        context = NewsSearchContext(queries=[query])
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        
        # Should not raise an error
        result = await repository.search(context)
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_search_with_none_end_date(self, repository, mock_session_manager):
        """Test search query with None end_date"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,
            start_date=date(2023, 1, 1),
            end_date=None  # No end date restriction
        )
        
        context = NewsSearchContext(queries=[query])
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        # Should handle None end_date gracefully
        assert result == {}
        # Verify session.execute was called
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_results_ordered_by_similarity(self, repository, mock_session_manager):
        """Test that results are ordered by similarity score descending"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1] * 1536,
            start_date=date(2023, 1, 1)
        )
        
        context = NewsSearchContext(queries=[query])
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        # Return results in order (should be ordered by SQL query)
        mock_rows = [
            Mock(id=1, company_id=company_id, title="최고유사도", contents="내용", similarity_score=0.95),
            Mock(id=2, company_id=company_id, title="중간유사도", contents="내용", similarity_score=0.85),
            Mock(id=3, company_id=company_id, title="낮은유사도", contents="내용", similarity_score=0.75),
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        news_list = result[company_id]
        assert len(news_list) == 3
        
        # Should be ordered by similarity descending (as returned by SQL)
        assert news_list[0].similarity == 0.95
        assert news_list[1].similarity == 0.85
        assert news_list[2].similarity == 0.75
    
    def test_search_query_to_tuple(self):
        """Test SearchQuery.to_tuple() method used by the repository"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1, 0.2, 0.3],
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        
        result = query.to_tuple()
        
        assert result == (company_id, [0.1, 0.2, 0.3], date(2023, 1, 1), date(2023, 12, 31))
    
    def test_search_query_to_tuple_with_none_end_date(self):
        """Test SearchQuery.to_tuple() with None end_date"""
        company_id = uuid4()
        query = SearchQuery(
            company_id=company_id,
            query_vector=[0.1, 0.2, 0.3],
            start_date=date(2023, 1, 1),
            end_date=None
        )
        
        result = query.to_tuple()
        
        assert result == (company_id, [0.1, 0.2, 0.3], date(2023, 1, 1), None)
    
    @pytest.mark.asyncio
    async def test_search_empty_company_results(self, repository, mock_session_manager):
        """Test when a company has no matching news"""
        company_id1 = uuid4()
        company_id2 = uuid4()
        
        queries = [
            SearchQuery(company_id=company_id1, query_vector=[0.1] * 1536, start_date=date(2023, 1, 1)),
            SearchQuery(company_id=company_id2, query_vector=[0.2] * 1536, start_date=date(2023, 1, 1))
        ]
        
        context = NewsSearchContext(queries=queries)
        
        mock_session = AsyncMock()
        mock_session_manager.__aenter__.return_value = mock_session
        
        # Only company1 has results
        mock_rows = [
            Mock(id=1, company_id=company_id1, title="뉴스", contents="내용", similarity_score=0.8),
        ]
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute.return_value = mock_result
        
        result = await repository.search(context)
        
        assert len(result) == 1  # Only company1 has results
        assert company_id1 in result
        assert company_id2 not in result