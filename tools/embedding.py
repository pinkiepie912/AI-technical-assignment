import os
from typing import List, Optional

import openai
from openai import OpenAI


def create_embeddings(
    texts: List[str], api_key: Optional[str] = None
) -> List[List[float]]:
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable"
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(model="text-embedding-3-small", input=texts)

        # Extract embedding vectors from response
        embeddings = [embedding.embedding for embedding in response.data]
        return embeddings

    except openai.OpenAIError as e:
        raise openai.OpenAIError(f"Failed to generate embeddings: {str(e)}") from e
