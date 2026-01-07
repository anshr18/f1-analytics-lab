"""
Chat API Schemas

Pydantic models for chat and RAG endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============================================================================
# Chat Session Schemas
# ============================================================================


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session"""

    user_id: Optional[str] = Field(None, description="Optional user identifier")
    title: Optional[str] = Field(None, description="Optional session title")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata")


class ChatSessionResponse(BaseModel):
    """Chat session details"""

    id: str = Field(..., description="Session UUID")
    user_id: Optional[str] = Field(None, description="User identifier")
    title: str = Field(..., description="Session title")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """List of chat sessions"""

    sessions: List[ChatSessionResponse] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total number of sessions")


# ============================================================================
# Chat Message Schemas
# ============================================================================


class ChatMessageSend(BaseModel):
    """Request to send a message"""

    message: str = Field(..., min_length=1, description="User message")
    use_rag: bool = Field(default=True, description="Whether to use RAG for context")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Min similarity score")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What was Max Verstappen's fastest lap at Bahrain?",
                "use_rag": True,
                "top_k": 5,
                "similarity_threshold": 0.7,
            }
        }


class ChatSourceResponse(BaseModel):
    """Source document used for RAG"""

    title: str = Field(..., description="Document title")
    doc_type: str = Field(..., description="Document type")
    similarity: float = Field(..., description="Similarity score")
    chunk_text: str = Field(..., description="Chunk text preview")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class ChatMessageResponse(BaseModel):
    """Chat message with metadata"""

    id: str = Field(..., description="Message UUID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Creation timestamp")


class ChatMessageSendResponse(BaseModel):
    """Response after sending a message"""

    message: ChatMessageResponse = Field(..., description="Assistant message")
    sources: Optional[List[ChatSourceResponse]] = Field(None, description="RAG sources")
    usage: Dict[str, int] = Field(..., description="Token usage stats")

    class Config:
        json_schema_extra = {
            "example": {
                "message": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "role": "assistant",
                    "content": "Max Verstappen's fastest lap at Bahrain was 1:31.447...",
                    "created_at": "2024-01-07T12:00:00",
                },
                "sources": [
                    {
                        "title": "Bahrain 2024 - Race",
                        "doc_type": "session_summary",
                        "similarity": 0.92,
                        "chunk_text": "The fastest lap was recorded by Max Verstappen...",
                        "metadata": {"session_id": "abc123"},
                    }
                ],
                "usage": {"prompt_tokens": 150, "completion_tokens": 50, "total_tokens": 200},
            }
        }


class ChatHistoryResponse(BaseModel):
    """Chat message history for a session"""

    session_id: str = Field(..., description="Session UUID")
    messages: List[ChatMessageResponse] = Field(..., description="Message history")
    total: int = Field(..., description="Total messages")


# ============================================================================
# RAG Query Schemas
# ============================================================================


class RAGQueryRequest(BaseModel):
    """One-off RAG query without session"""

    question: str = Field(..., min_length=1, description="Question to answer")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Min similarity")
    doc_type: Optional[str] = Field(None, description="Filter by document type")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Who had the best lap time in Bahrain 2024?",
                "top_k": 5,
                "similarity_threshold": 0.7,
                "doc_type": "session_summary",
            }
        }


class RAGQueryResponse(BaseModel):
    """RAG query response"""

    answer: str = Field(..., description="Generated answer")
    sources: List[ChatSourceResponse] = Field(..., description="Source documents")
    num_sources: int = Field(..., description="Number of sources retrieved")
    usage: Dict[str, int] = Field(..., description="Token usage")
    model: str = Field(..., description="Model used")


# ============================================================================
# Document Schemas
# ============================================================================


class DocumentIngestRequest(BaseModel):
    """Request to ingest a document"""

    title: str = Field(..., min_length=1, description="Document title")
    content: str = Field(..., min_length=1, description="Document content")
    doc_type: str = Field(default="custom", description="Document type")
    source_url: Optional[str] = Field(None, description="Source URL")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata")


class DocumentResponse(BaseModel):
    """Document details"""

    id: str = Field(..., description="Document UUID")
    doc_type: str = Field(..., description="Document type")
    title: str = Field(..., description="Document title")
    source_url: Optional[str] = Field(None, description="Source URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class DocumentCountResponse(BaseModel):
    """Document counts by type"""

    counts: Dict[str, int] = Field(..., description="Count by document type")
    total: int = Field(..., description="Total documents")


class BulkIngestRequest(BaseModel):
    """Request to bulk ingest sessions"""

    limit: int = Field(default=10, ge=1, le=100, description="Number of sessions to ingest")


class BulkIngestResponse(BaseModel):
    """Bulk ingest results"""

    ingested_count: int = Field(..., description="Number of documents created")
    document_ids: List[str] = Field(..., description="Created document IDs")
