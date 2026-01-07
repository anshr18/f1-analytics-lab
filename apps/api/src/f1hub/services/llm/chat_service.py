"""
Chat Service

Manage chat sessions and message history with RAG integration.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from f1hub.db.models.llm import ChatSession, ChatMessage
from f1hub.services.llm.rag_service import RAGService


class ChatService:
    """Service for managing chat sessions with RAG-powered responses."""

    def __init__(self, db: Session):
        """
        Initialize chat service.

        Args:
            db: Database session
        """
        self.db = db
        self.rag_service = RAGService(db)

    def create_session(
        self,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: Optional user identifier
            title: Optional session title
            metadata: Optional session metadata

        Returns:
            Created ChatSession
        """
        session = ChatSession(
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            metadata=metadata or {},
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get chat session by ID.

        Args:
            session_id: Session UUID

        Returns:
            ChatSession or None if not found
        """
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChatSession]:
        """
        List chat sessions.

        Args:
            user_id: Optional filter by user
            limit: Maximum number of sessions
            offset: Offset for pagination

        Returns:
            List of ChatSession objects
        """
        query = self.db.query(ChatSession)

        if user_id:
            query = query.filter(ChatSession.user_id == user_id)

        return (
            query.order_by(desc(ChatSession.updated_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        retrieved_chunks: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """
        Add message to chat session.

        Args:
            session_id: Session UUID
            role: Message role (user, assistant, system)
            content: Message content
            retrieved_chunks: Optional list of retrieved chunk IDs
            metadata: Optional message metadata

        Returns:
            Created ChatMessage
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            retrieved_chunks=retrieved_chunks or [],
            metadata=metadata or {},
        )
        self.db.add(message)

        # Update session timestamp
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatMessage]:
        """
        Get messages for a session.

        Args:
            session_id: Session UUID
            limit: Optional limit on number of messages

        Returns:
            List of ChatMessage objects ordered by creation time
        """
        query = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def send_message(
        self,
        session_id: str,
        user_message: str,
        use_rag: bool = True,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response with RAG.

        Args:
            session_id: Session UUID
            user_message: User's message
            use_rag: Whether to use RAG for context
            top_k: Number of context chunks to retrieve
            similarity_threshold: Minimum similarity for retrieval

        Returns:
            Dict with assistant message and metadata
        """
        # Add user message to history
        self.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        if use_rag:
            # Use RAG for response
            rag_response = self.rag_service.query(
                question=user_message,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                include_sources=True,
            )

            assistant_message = rag_response["answer"]
            retrieved_chunk_ids = [
                source.get("embedding_id") for source in rag_response.get("sources", [])
            ]

            # Add assistant message with retrieved chunks
            message = self.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message,
                retrieved_chunks=retrieved_chunk_ids,
                metadata={
                    "num_sources": rag_response["num_sources"],
                    "model": rag_response["model"],
                    "usage": rag_response["usage"],
                },
            )

            return {
                "message": {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
                "sources": rag_response.get("sources", []),
                "usage": rag_response["usage"],
            }
        else:
            # Simple completion without RAG
            # Get recent message history for context
            recent_messages = self.get_session_messages(session_id, limit=10)
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ]

            completion = self.rag_service.llm_service.generate_completion(messages)

            # Add assistant message
            message = self.add_message(
                session_id=session_id,
                role="assistant",
                content=completion["content"],
                metadata={"model": completion["model"], "usage": completion["usage"]},
            )

            return {
                "message": {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
                "usage": completion["usage"],
            }

    async def send_message_async(
        self,
        session_id: str,
        user_message: str,
        use_rag: bool = True,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response asynchronously.

        Args:
            session_id: Session UUID
            user_message: User's message
            use_rag: Whether to use RAG for context
            top_k: Number of context chunks to retrieve
            similarity_threshold: Minimum similarity for retrieval

        Returns:
            Dict with assistant message and metadata
        """
        # Add user message to history
        self.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        if use_rag:
            # Use RAG for response
            rag_response = await self.rag_service.query_async(
                question=user_message,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                include_sources=True,
            )

            assistant_message = rag_response["answer"]
            retrieved_chunk_ids = [
                source.get("embedding_id") for source in rag_response.get("sources", [])
            ]

            # Add assistant message with retrieved chunks
            message = self.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message,
                retrieved_chunks=retrieved_chunk_ids,
                metadata={
                    "num_sources": rag_response["num_sources"],
                    "model": rag_response["model"],
                    "usage": rag_response["usage"],
                },
            )

            return {
                "message": {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
                "sources": rag_response.get("sources", []),
                "usage": rag_response["usage"],
            }
        else:
            # Simple completion without RAG
            recent_messages = self.get_session_messages(session_id, limit=10)
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ]

            completion = await self.rag_service.llm_service.generate_completion_async(messages)

            # Add assistant message
            message = self.add_message(
                session_id=session_id,
                role="assistant",
                content=completion["content"],
                metadata={"model": completion["model"], "usage": completion["usage"]},
            )

            return {
                "message": {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
                "usage": completion["usage"],
            }

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session and all its messages.

        Args:
            session_id: Session UUID

        Returns:
            True if deleted, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Delete all messages first
        self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()

        # Delete session
        self.db.delete(session)
        self.db.commit()

        return True
