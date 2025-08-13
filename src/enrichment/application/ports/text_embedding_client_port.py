from abc import ABC, abstractmethod
from typing import List


class TextEmbeddingClientPort(ABC):
    """Abstract interface for embedding generation clients."""

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts.

        Args:
            texts: List of input texts to generate embeddings for

        Returns:
            List of embedding vectors, each as a list of float values

        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        ...
