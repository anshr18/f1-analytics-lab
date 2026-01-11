"""
F1 Intelligence Hub - LLM/RAG Database Models

LLM and RAG system: Document, Embedding, ChatSession, ChatMessage
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Document.

    Stores documents for RAG (regulations, articles, transcripts, etc.).
    """

    __tablename__ = "documents"

    doc_type = Column(String(50), nullable=False)  # regulation, article, transcript, session_summary
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Full document content
    source_url = Column(String(1000), nullable=True)  # Original source URL

    # Metadata (e.g., year, race, author, etc.) - renamed to avoid SQLAlchemy reserved name
    doc_metadata = Column(JSONB, nullable=True)

    # Relationships
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(type={self.doc_type}, title={self.title[:50]})>"


class Embedding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Document Embedding.

    Stores vector embeddings for document chunks (for semantic search).
    """

    __tablename__ = "embeddings"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk within document
    chunk_text = Column(Text, nullable=False)  # Text content of this chunk

    # Vector embedding (OpenAI text-embedding-3-small = 1536 dimensions)
    embedding = Column(Vector(1536), nullable=False)

    # Chunk metadata
    chunk_metadata = Column(JSONB, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(document_id={self.document_id}, chunk={self.chunk_index})>"


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Chat Session.

    Represents a user's chat conversation with the RAG system.
    """

    __tablename__ = "chat_sessions"

    session_name = Column(String(200), nullable=True)  # Optional user-provided name
    user_id = Column(String(100), nullable=True)  # Placeholder for Phase 3 auth

    # Session metadata
    session_metadata = Column(JSONB, nullable=True)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, name={self.session_name})>"


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Chat Message.

    Stores individual messages within a chat session.
    """

    __tablename__ = "chat_messages"

    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # RAG metadata
    retrieved_chunks = Column(JSONB, nullable=True)  # Document chunks used for this response
    model_used = Column(String(100), nullable=True)  # e.g., "gpt-4-turbo"

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(session_id={self.session_id}, role={self.role})>"
