from typing import List

import openai
from openai import AsyncOpenAI

from enrichment.application.exceptions.embedding_exception import (
    EmbeddingConnectionError,
    EmbeddingGenerationError,
)
from enrichment.application.ports.text_embedding_client_port import (
    TextEmbeddingClientPort,
)


class OpenAIEmbeddingClient(TextEmbeddingClientPort):
    """OpenAI implementation of the EmbeddingClient interface."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts using OpenAI's API.

        Args:
            texts: List of input texts to generate embeddings for

        Returns:
            List of embedding vectors, each as a list of float values

        Raises:
            EmbeddingGenerationError: If embedding generation fails
            EmbeddingConnectionError: If connection to OpenAI fails
        """
        if not texts:
            return []

        # Filter out empty texts and track their original positions
        filtered_texts = []
        text_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                filtered_texts.append(text.strip())
                text_indices.append(i)

        if not filtered_texts:
            raise EmbeddingGenerationError(
                str(texts), "All input texts are empty or None"
            )

        try:
            response = await self.client.embeddings.create(
                input=filtered_texts, model=self.model
            )

            if not response.data or len(response.data) != len(filtered_texts):
                raise EmbeddingGenerationError(
                    str(texts), "OpenAI returned unexpected number of embeddings"
                )

            embeddings = [[] for _ in texts]
            for i, embedding_data in enumerate(response.data):
                original_index = text_indices[i]
                embeddings[original_index] = embedding_data.embedding

            return embeddings

        except openai.AuthenticationError as e:
            raise EmbeddingConnectionError("OpenAI", f"Authentication failed: {str(e)}")

        except openai.RateLimitError as e:
            raise EmbeddingConnectionError("OpenAI", f"Rate limit exceeded: {str(e)}")

        except openai.APIConnectionError as e:
            raise EmbeddingConnectionError("OpenAI", f"API connection failed: {str(e)}")

        except openai.APIError as e:
            raise EmbeddingGenerationError(str(texts), f"OpenAI API error: {str(e)}")

        except Exception as e:
            raise EmbeddingGenerationError(str(texts), f"Unexpected error: {str(e)}")
