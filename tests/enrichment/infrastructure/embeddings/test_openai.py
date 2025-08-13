from typing import List
from unittest.mock import AsyncMock, Mock

import openai
import pytest
from openai.types import CreateEmbeddingResponse
from openai.types.create_embedding_response import Usage
from openai.types.embedding import Embedding

from enrichment.application.exceptions.embedding_exception import (
    EmbeddingConnectionError,
    EmbeddingGenerationError,
)
from enrichment.infrastructure.embeddings.openai import OpenAIEmbeddingClient


class TestOpenAIEmbedding:
    """Test suite for OpenAIEmbedding class."""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client."""
        return Mock()

    @pytest.fixture
    def openai_embedding(self, mock_client):
        """Create OpenAIEmbedding instance with mocked client."""
        embedding_client = OpenAIEmbeddingClient(api_key="test-api-key")
        embedding_client.client = mock_client
        return embedding_client

    def create_mock_embedding_response(
        self, embeddings: List[List[float]], model: str = "text-embedding-3-small"
    ) -> CreateEmbeddingResponse:
        """Create a mock embedding response from OpenAI API."""
        embedding_objects = [
            Embedding(embedding=emb, index=i, object="embedding")
            for i, emb in enumerate(embeddings)
        ]

        return CreateEmbeddingResponse(
            data=embedding_objects,
            model=model,
            object="list",
            usage=Usage(prompt_tokens=10, total_tokens=10),
        )

    @pytest.mark.asyncio
    async def test_successful_single_text_embedding(
        self, openai_embedding, mock_client
    ):
        """Test successful embedding generation for single text."""
        # Arrange
        texts = ["Hello world"]
        expected_embedding = [0.1, 0.2, 0.3, 0.4]
        mock_response = self.create_mock_embedding_response([expected_embedding])
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await openai_embedding.generate_embeddings(texts)

        # Assert
        assert len(result) == 1
        assert result[0] == expected_embedding
        mock_client.embeddings.create.assert_called_once_with(
            input=["Hello world"], model="text-embedding-3-small"
        )

    @pytest.mark.asyncio
    async def test_successful_multiple_text_embedding(
        self, openai_embedding, mock_client
    ):
        """Test successful embedding generation for multiple texts."""
        # Arrange
        texts = ["First text", "Second text", "Third text"]
        expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        mock_response = self.create_mock_embedding_response(expected_embeddings)
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await openai_embedding.generate_embeddings(texts)

        # Assert
        assert len(result) == 3
        assert result == expected_embeddings
        mock_client.embeddings.create.assert_called_once_with(
            input=texts, model="text-embedding-3-small"
        )

    @pytest.mark.asyncio
    async def test_empty_input_list(self, openai_embedding):
        """Test behavior with empty input list."""
        # Act
        result = await openai_embedding.generate_embeddings([])

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_all_empty_texts_raises_error(self, openai_embedding):
        """Test that all empty/whitespace texts raise EmbeddingGenerationError."""
        # Arrange
        texts = ["", "   ", "\t\n", None]

        # Act & Assert
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert "All input texts are empty or None" in str(exc_info.value)
        assert exc_info.value.text == str(texts)

    @pytest.mark.asyncio
    async def test_mixed_empty_and_valid_texts(self, openai_embedding, mock_client):
        """Test handling of mixed empty and valid texts."""
        # Arrange
        texts = ["", "Valid text", "   ", "Another valid text", "\t"]
        expected_embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_response = self.create_mock_embedding_response(expected_embeddings)
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await openai_embedding.generate_embeddings(texts)

        # Assert
        assert len(result) == 5
        assert result[0] == []  # Empty for first empty text
        assert result[1] == expected_embeddings[0]  # First valid embedding
        assert result[2] == []  # Empty for second empty text
        assert result[3] == expected_embeddings[1]  # Second valid embedding
        assert result[4] == []  # Empty for third empty text

        mock_client.embeddings.create.assert_called_once_with(
            input=["Valid text", "Another valid text"], model="text-embedding-3-small"
        )

    @pytest.mark.asyncio
    async def test_authentication_error(self, openai_embedding, mock_client):
        """Test handling of OpenAI authentication errors."""
        # Arrange
        texts = ["Test text"]
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.embeddings.create = AsyncMock(
            side_effect=openai.AuthenticationError(
                "Invalid API key", response=mock_response, body="Authentication failed"
            )
        )

        # Act & Assert
        with pytest.raises(EmbeddingConnectionError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.service_name == "OpenAI"
        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, openai_embedding, mock_client):
        """Test handling of OpenAI rate limit errors."""
        # Arrange
        texts = ["Test text"]
        mock_response = Mock()
        mock_response.status_code = 429
        mock_client.embeddings.create = AsyncMock(
            side_effect=openai.RateLimitError(
                "Rate limit exceeded",
                response=mock_response,
                body="Rate limit exceeded",
            )
        )

        # Act & Assert
        with pytest.raises(EmbeddingConnectionError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.service_name == "OpenAI"
        assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_api_connection_error(self, openai_embedding, mock_client):
        """Test handling of OpenAI API connection errors."""
        # Arrange
        texts = ["Test text"]
        mock_client.embeddings.create = AsyncMock(
            side_effect=openai.APIConnectionError(request=Mock())
        )

        # Act & Assert
        with pytest.raises(EmbeddingConnectionError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.service_name == "OpenAI"
        assert "API connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_general_api_error(self, openai_embedding, mock_client):
        """Test handling of general OpenAI API errors."""
        # Arrange
        texts = ["Test text"]
        mock_request = Mock()
        mock_client.embeddings.create = AsyncMock(
            side_effect=openai.APIError(
                "General API error", request=mock_request, body="General API error"
            )
        )

        # Act & Assert
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.text == str(texts)
        assert "OpenAI API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unexpected_error(self, openai_embedding, mock_client):
        """Test handling of unexpected errors."""
        # Arrange
        texts = ["Test text"]
        mock_client.embeddings.create = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )

        # Act & Assert
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.text == str(texts)
        assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_response_data(self, openai_embedding, mock_client):
        """Test handling when OpenAI returns empty response data."""
        # Arrange
        texts = ["Test text"]
        mock_response = CreateEmbeddingResponse(
            data=[],
            model="text-embedding-3-small",
            object="list",
            usage=Usage(prompt_tokens=10, total_tokens=10),
        )
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.text == str(texts)
        assert "OpenAI returned unexpected number of embeddings" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mismatched_response_count(self, openai_embedding, mock_client):
        """Test handling when OpenAI returns wrong number of embeddings."""
        # Arrange
        texts = ["First text", "Second text"]
        # Return only one embedding for two texts
        expected_embeddings = [[0.1, 0.2, 0.3]]
        mock_response = self.create_mock_embedding_response(expected_embeddings)
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            await openai_embedding.generate_embeddings(texts)

        assert exc_info.value.text == str(texts)
        assert "OpenAI returned unexpected number of embeddings" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_custom_model_parameter(self, mock_client):
        """Test OpenAIEmbedding with custom model parameter."""
        # Arrange
        custom_model = "text-embedding-ada-002"
        embedding_client = OpenAIEmbeddingClient(
            api_key="test-api-key", model=custom_model
        )
        embedding_client.client = mock_client

        texts = ["Test text"]
        expected_embedding = [0.1, 0.2, 0.3]
        mock_response = self.create_mock_embedding_response(
            [expected_embedding], custom_model
        )
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await embedding_client.generate_embeddings(texts)

        # Assert
        assert result == [expected_embedding]
        mock_client.embeddings.create.assert_called_once_with(
            input=texts, model=custom_model
        )

    @pytest.mark.asyncio
    async def test_initialization_with_default_model(self):
        """Test OpenAIEmbedding initialization with default model."""
        # Act
        embedding_client = OpenAIEmbeddingClient(api_key="test-api-key")

        # Assert
        assert embedding_client.model == "text-embedding-3-small"
        assert embedding_client.client is not None

    @pytest.mark.asyncio
    async def test_text_preprocessing_whitespace_stripping(
        self, openai_embedding, mock_client
    ):
        """Test that input texts are properly stripped of whitespace."""
        # Arrange
        texts = ["  Text with spaces  ", "\tTabbed text\n", " Normal text"]
        expected_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        mock_response = self.create_mock_embedding_response(expected_embeddings)
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await openai_embedding.generate_embeddings(texts)

        # Assert
        assert len(result) == 3
        assert result == expected_embeddings
        # Verify that the API was called with stripped texts
        mock_client.embeddings.create.assert_called_once_with(
            input=["Text with spaces", "Tabbed text", "Normal text"],
            model="text-embedding-3-small",
        )

    @pytest.mark.asyncio
    async def test_large_batch_processing(self, openai_embedding, mock_client):
        """Test processing of large batch of texts."""
        # Arrange
        texts = [f"Text number {i}" for i in range(100)]
        expected_embeddings = [[float(i), float(i + 1)] for i in range(100)]
        mock_response = self.create_mock_embedding_response(expected_embeddings)
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await openai_embedding.generate_embeddings(texts)

        # Assert
        assert len(result) == 100
        assert result == expected_embeddings
        mock_client.embeddings.create.assert_called_once_with(
            input=texts, model="text-embedding-3-small"
        )

