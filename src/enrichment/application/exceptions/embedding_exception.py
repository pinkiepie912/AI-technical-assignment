from typing import Optional


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.details = details
        super().__init__(message)


class EmbeddingGenerationError(EmbeddingError):
    """Exception raised when embedding generation fails."""

    def __init__(self, text: str, details: str):
        message = f"Failed to generate embedding for text: {details}"
        super().__init__(message, details)
        self.text = text


class EmbeddingConnectionError(EmbeddingError):
    """Exception raised when connection to embedding service fails."""

    def __init__(self, service_name: str, details: str):
        message = f"Connection to {service_name} failed: {details}"
        super().__init__(message, details)
        self.service_name = service_name
