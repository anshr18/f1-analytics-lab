"""
Embedding Service

Generate embeddings for text using OpenAI's embedding models.
"""

from typing import List
import numpy as np
from openai import OpenAI, AsyncOpenAI
from f1hub.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        """Initialize embedding service with OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.embedding_dim = 1536  # text-embedding-3-small dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding

    async def generate_embedding_async(self, text: str) -> List[float]:
        """
        Generate embedding for a single text asynchronously.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        response = await self.async_client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        # Sort by index to maintain order
        embeddings_with_index = [(item.index, item.embedding) for item in response.data]
        embeddings_with_index.sort(key=lambda x: x[0])

        return [emb for _, emb in embeddings_with_index]

    async def generate_embeddings_batch_async(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts asynchronously.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        response = await self.async_client.embeddings.create(
            model=self.model,
            input=texts,
        )

        # Sort by index to maintain order
        embeddings_with_index = [(item.index, item.embedding) for item in response.data]
        embeddings_with_index.sort(key=lambda x: x[0])

        return [emb for _, emb in embeddings_with_index]

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
