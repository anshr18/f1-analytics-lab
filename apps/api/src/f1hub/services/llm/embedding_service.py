"""
Embedding Service

Generate embeddings for text using Google Gemini's embedding model.
"""

from typing import List
import numpy as np
import google.generativeai as genai
from f1hub.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Google Gemini."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = f"models/{settings.GEMINI_EMBEDDING_MODEL}"
        self.embedding_dim = 768  # text-embedding-004 dimension

    def generate_embedding(self, text: str) -> List[float]:
        result = genai.embed_content(model=self.model, content=text)
        return result["embedding"]

    async def generate_embedding_async(self, text: str) -> List[float]:
        # google-generativeai embed_content is synchronous; run in executor for async contexts
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embedding, text)

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return [self.generate_embedding(t) for t in texts]

    async def generate_embeddings_batch_async(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embeddings_batch, texts)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
