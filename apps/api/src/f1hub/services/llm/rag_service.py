"""
RAG Service

Retrieval-Augmented Generation service for semantic search and context retrieval.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from f1hub.db.models.llm import Document, Embedding
from f1hub.services.llm.embedding_service import EmbeddingService
from f1hub.services.llm.llm_service import LLMService


class RAGService:
    """Service for RAG-based question answering with semantic search."""

    def __init__(self, db: Session):
        """
        Initialize RAG service.

        Args:
            db: Database session
        """
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.7,
        doc_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using pgvector cosine similarity.

        Args:
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0-1)
            doc_type: Optional document type filter

        Returns:
            List of relevant document chunks with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.embedding_service.generate_embedding(query)

        # Build SQL query for vector similarity search
        # Using cosine distance operator <=> (lower is more similar)
        sql = text("""
            SELECT
                e.id,
                e.document_id,
                e.chunk_text,
                e.chunk_index,
                e.chunk_metadata,
                d.title,
                d.doc_type,
                d.source_url,
                d.metadata,
                1 - (e.embedding <=> :query_embedding::vector) as similarity
            FROM embeddings e
            JOIN documents d ON e.document_id = d.id
            WHERE 1 - (e.embedding <=> :query_embedding::vector) >= :threshold
            """ + ("AND d.doc_type = :doc_type" if doc_type else "") + """
            ORDER BY e.embedding <=> :query_embedding::vector
            LIMIT :limit
        """)

        params = {
            "query_embedding": str(query_embedding),
            "threshold": similarity_threshold,
            "limit": limit,
        }
        if doc_type:
            params["doc_type"] = doc_type

        results = self.db.execute(sql, params).fetchall()

        return [
            {
                "embedding_id": str(row.id),
                "document_id": str(row.document_id),
                "chunk_text": row.chunk_text,
                "chunk_index": row.chunk_index,
                "chunk_metadata": row.chunk_metadata or {},
                "document_title": row.title,
                "doc_type": row.doc_type,
                "source_url": row.source_url,
                "document_metadata": row.metadata or {},
                "similarity": float(row.similarity),
            }
            for row in results
        ]

    def build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Build context string from search results for LLM prompt.

        Args:
            search_results: Results from semantic_search()

        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant context found."

        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}: {result['document_title']}]\n"
                f"{result['chunk_text']}\n"
            )

        return "\n".join(context_parts)

    def build_rag_prompt(
        self,
        user_query: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Build prompt messages for RAG-based completion.

        Args:
            user_query: User's question
            context: Retrieved context from semantic search
            system_prompt: Optional custom system prompt

        Returns:
            List of message dicts for LLM
        """
        if system_prompt is None:
            system_prompt = """You are an expert F1 analytics assistant. Answer questions about Formula 1 races, drivers, strategies, and performance data using the provided context.

Guidelines:
- Use the context to provide accurate, data-driven answers
- If the context doesn't contain enough information, acknowledge limitations
- Include specific data points (lap times, positions, tire compounds) when relevant
- Be concise but thorough
- Format responses clearly with bullet points or numbered lists when appropriate"""

        user_message = f"""Context from F1 data:

{context}

---

User Question: {user_query}

Please answer the question using the context provided above."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    def query(
        self,
        question: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        doc_type: Optional[str] = None,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform RAG query: search + generate answer.

        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            similarity_threshold: Minimum similarity for retrieval
            doc_type: Optional document type filter
            include_sources: Whether to include source documents in response

        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 1: Semantic search
        search_results = self.semantic_search(
            query=question,
            limit=top_k,
            similarity_threshold=similarity_threshold,
            doc_type=doc_type,
        )

        # Step 2: Build context
        context = self.build_context(search_results)

        # Step 3: Build prompt
        messages = self.build_rag_prompt(question, context)

        # Step 4: Generate answer
        completion = self.llm_service.generate_completion(messages)

        # Step 5: Prepare response
        response = {
            "answer": completion["content"],
            "usage": completion["usage"],
            "model": completion["model"],
            "num_sources": len(search_results),
        }

        if include_sources:
            response["sources"] = [
                {
                    "title": result["document_title"],
                    "doc_type": result["doc_type"],
                    "similarity": result["similarity"],
                    "chunk_text": result["chunk_text"][:200] + "...",  # Preview
                    "metadata": result["document_metadata"],
                }
                for result in search_results
            ]

        return response

    async def query_async(
        self,
        question: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        doc_type: Optional[str] = None,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform RAG query asynchronously.

        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            similarity_threshold: Minimum similarity for retrieval
            doc_type: Optional document type filter
            include_sources: Whether to include source documents in response

        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 1: Semantic search (sync - DB operation)
        search_results = self.semantic_search(
            query=question,
            limit=top_k,
            similarity_threshold=similarity_threshold,
            doc_type=doc_type,
        )

        # Step 2: Build context
        context = self.build_context(search_results)

        # Step 3: Build prompt
        messages = self.build_rag_prompt(question, context)

        # Step 4: Generate answer asynchronously
        completion = await self.llm_service.generate_completion_async(messages)

        # Step 5: Prepare response
        response = {
            "answer": completion["content"],
            "usage": completion["usage"],
            "model": completion["model"],
            "num_sources": len(search_results),
        }

        if include_sources:
            response["sources"] = [
                {
                    "title": result["document_title"],
                    "doc_type": result["doc_type"],
                    "similarity": result["similarity"],
                    "chunk_text": result["chunk_text"][:200] + "...",
                    "metadata": result["document_metadata"],
                }
                for result in search_results
            ]

        return response
