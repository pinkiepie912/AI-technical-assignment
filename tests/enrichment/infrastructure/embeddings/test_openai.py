"""Test cases for OpenAI embedding service"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import openai

from enrichment.infrastructure.embeddings.openai import OpenAIEmbeddingClient
from enrichment.application.exceptions.embedding_exception import (
    EmbeddingConnectionError,
    EmbeddingGenerationError
)


class TestOpenAIEmbeddingClient:
    @pytest.fixture
    def client(self):
        return OpenAIEmbeddingClient(api_key="test-api-key", model="text-embedding-3-small")
    
    @pytest.fixture
    def mock_response(self):
        """Mock OpenAI API response"""
        response = Mock()
        response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        return response

    def test_init(self):
        client = OpenAIEmbeddingClient(api_key="test-key")
        assert client.model == "text-embedding-3-small"
        assert client.client is not None
    
    def test_init_with_custom_model(self):
        client = OpenAIEmbeddingClient(api_key="test-key", model="text-embedding-ada-002")
        assert client.model == "text-embedding-ada-002"

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_input(self, client):
        result = await client.generate_embeddings([])
        assert result == []
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_all_empty_texts(self, client):
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await client.generate_embeddings(["", "   ", None])
        
        assert "All input texts are empty or None" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, client, mock_response):
        texts = ["Hello world", "Testing embeddings"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await client.generate_embeddings(texts)
            
            mock_create.assert_called_once_with(
                input=["Hello world", "Testing embeddings"],
                model="text-embedding-3-small"
            )
            
            assert len(result) == 2
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_with_empty_texts_mixed(self, client):
        texts = ["Hello world", "", "Testing embeddings", "   "]
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await client.generate_embeddings(texts)
            
            # Only non-empty texts should be sent to API
            mock_create.assert_called_once_with(
                input=["Hello world", "Testing embeddings"],
                model="text-embedding-3-small"
            )
            
            assert len(result) == 4
            assert result[0] == [0.1, 0.2, 0.3]  # First text
            assert result[1] == []  # Empty text
            assert result[2] == [0.4, 0.5, 0.6]  # Third text
            assert result[3] == []  # Empty text
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_unexpected_response_length(self, client):
        texts = ["Hello world", "Testing embeddings"]
        
        # Response with wrong number of embeddings
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]  # Only 1 embedding for 2 texts
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "unexpected number of embeddings" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_no_data(self, client):
        texts = ["Hello world"]
        
        # Response with no data
        mock_response = Mock()
        mock_response.data = []
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "unexpected number of embeddings" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_authentication_error(self, client):
        texts = ["Hello world"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = openai.AuthenticationError(
                message="Invalid API key", response=Mock(), body=None
            )
            
            with pytest.raises(EmbeddingConnectionError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "Authentication failed" in str(exc_info.value)
            assert exc_info.value.service_name == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_rate_limit_error(self, client):
        texts = ["Hello world"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = openai.RateLimitError(
                message="Rate limit exceeded", response=Mock(), body=None
            )
            
            with pytest.raises(EmbeddingConnectionError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "Rate limit exceeded" in str(exc_info.value)
            assert exc_info.value.service_name == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_api_connection_error(self, client):
        texts = ["Hello world"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = openai.APIConnectionError(request=Mock())
            
            with pytest.raises(EmbeddingConnectionError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "API connection failed" in str(exc_info.value)
            assert exc_info.value.service_name == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_api_error(self, client):
        texts = ["Hello world"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = openai.APIError(
                message="API error occurred", request=Mock(), body=None
            )
            
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "OpenAI API error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_unexpected_error(self, client):
        texts = ["Hello world"]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValueError("Unexpected error")
            
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                await client.generate_embeddings(texts)
            
            assert "Unexpected error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_text_preprocessing(self, client):
        texts = ["  Hello world  ", "\t\nTesting\n\t", "Normal text"]
        
        # Create response with correct number of embeddings (3)
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
            Mock(embedding=[0.7, 0.8, 0.9])
        ]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            await client.generate_embeddings(texts)
            
            # Check that texts are stripped before sending to API
            mock_create.assert_called_once_with(
                input=["Hello world", "Testing", "Normal text"],
                model="text-embedding-3-small"
            )
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_large_batch(self, client):
        """Test handling of large batches of texts"""
        texts = [f"Text number {i}" for i in range(100)]
        
        # Create mock response with 100 embeddings
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3]) for _ in range(100)]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await client.generate_embeddings(texts)
            
            assert len(result) == 100
            assert all(embedding == [0.1, 0.2, 0.3] for embedding in result)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_single_text(self, client):
        """Test with single text input"""
        texts = ["Single text"]
        
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await client.generate_embeddings(texts)
            
            assert len(result) == 1
            assert result[0] == [0.1, 0.2, 0.3]
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_unicode_text(self, client):
        """Test with unicode and special characters"""
        texts = ["한글 텍스트", "🚀 Emoji text", "Special chars: !@#$%^&*()"]
        
        # Create response with correct number of embeddings (3)
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
            Mock(embedding=[0.7, 0.8, 0.9])
        ]
        
        with patch.object(client.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            result = await client.generate_embeddings(texts)
            
            mock_create.assert_called_once_with(
                input=texts,
                model="text-embedding-3-small"
            )
            
            assert len(result) == 3