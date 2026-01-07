"""
Chat API Endpoints

Endpoints for RAG-powered chat and question answering.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from f1hub.core.dependencies import get_db
from f1hub.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageSend,
    ChatMessageSendResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    DocumentIngestRequest,
    DocumentResponse,
    DocumentCountResponse,
    BulkIngestRequest,
    BulkIngestResponse,
)
from f1hub.services.llm import ChatService, RAGService
from f1hub.services.llm.document_ingestor import DocumentIngestor

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: ChatSessionCreate,
    db: Session = Depends(get_db),
) -> ChatSessionResponse:
    """
    Create a new chat session.

    Creates a new chat session that can be used to maintain conversation context
    and message history with the AI assistant.

    Args:
        request: Session creation parameters
        db: Database session

    Returns:
        Created chat session details

    Raises:
        HTTPException: If session creation fails
    """
    try:
        chat_service = ChatService(db)
        session = chat_service.create_session(
            user_id=request.user_id,
            title=request.title,
            metadata=request.metadata,
        )

        return ChatSessionResponse(
            id=str(session.id),
            user_id=session.user_id,
            title=session.title,
            metadata=session.metadata,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}",
        )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    user_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> ChatSessionListResponse:
    """
    List chat sessions.

    Retrieves a list of chat sessions, optionally filtered by user.

    Args:
        user_id: Optional filter by user ID
        limit: Maximum number of sessions to return
        offset: Offset for pagination
        db: Database session

    Returns:
        List of chat sessions

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        chat_service = ChatService(db)
        sessions = chat_service.list_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

        return ChatSessionListResponse(
            sessions=[
                ChatSessionResponse(
                    id=str(s.id),
                    user_id=s.user_id,
                    title=s.title,
                    metadata=s.metadata,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                )
                for s in sessions
            ],
            total=len(sessions),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}",
        )


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    limit: int | None = None,
    db: Session = Depends(get_db),
) -> ChatHistoryResponse:
    """
    Get chat history for a session.

    Retrieves all messages in a chat session.

    Args:
        session_id: Session UUID
        limit: Optional limit on number of messages
        db: Database session

    Returns:
        Chat message history

    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        chat_service = ChatService(db)

        # Check if session exists
        session = chat_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        messages = chat_service.get_session_messages(session_id, limit=limit)

        return ChatHistoryResponse(
            session_id=session_id,
            messages=[
                ChatMessageResponse(
                    id=str(msg.id),
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in messages
            ],
            total=len(messages),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session history: {str(e)}",
        )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageSendResponse)
async def send_message(
    session_id: str,
    request: ChatMessageSend,
    db: Session = Depends(get_db),
) -> ChatMessageSendResponse:
    """
    Send a message in a chat session.

    Sends a user message and receives an AI-generated response with optional
    RAG context from F1 data.

    Args:
        session_id: Session UUID
        request: Message and RAG parameters
        db: Database session

    Returns:
        Assistant response with sources

    Raises:
        HTTPException: If session not found or processing fails
    """
    try:
        chat_service = ChatService(db)

        # Check if session exists
        session = chat_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        # Send message and get response
        response = await chat_service.send_message_async(
            session_id=session_id,
            user_message=request.message,
            use_rag=request.use_rag,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
        )

        return ChatMessageSendResponse(
            message=response["message"],
            sources=response.get("sources"),
            usage=response["usage"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a chat session.

    Deletes a chat session and all its messages.

    Args:
        session_id: Session UUID
        db: Database session

    Raises:
        HTTPException: If session not found or deletion fails
    """
    try:
        chat_service = ChatService(db)
        deleted = chat_service.delete_session(session_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}",
        )


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
) -> RAGQueryResponse:
    """
    Perform a one-off RAG query without creating a session.

    Answers a question using RAG with semantic search over F1 data.
    Useful for stateless queries that don't require conversation context.

    Args:
        request: Query parameters
        db: Database session

    Returns:
        Answer with source attribution

    Raises:
        HTTPException: If query processing fails
    """
    try:
        rag_service = RAGService(db)

        response = await rag_service.query_async(
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            doc_type=request.doc_type,
            include_sources=True,
        )

        return RAGQueryResponse(
            answer=response["answer"],
            sources=response["sources"],
            num_sources=response["num_sources"],
            usage=response["usage"],
            model=response["model"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process RAG query: {str(e)}",
        )


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    request: DocumentIngestRequest,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Ingest a custom document.

    Creates embeddings for a custom text document and makes it searchable.

    Args:
        request: Document details
        db: Database session

    Returns:
        Created document details

    Raises:
        HTTPException: If ingestion fails
    """
    try:
        ingestor = DocumentIngestor(db)

        doc = ingestor.ingest_custom_document(
            title=request.title,
            content=request.content,
            doc_type=request.doc_type,
            source_url=request.source_url,
            metadata=request.metadata,
        )

        return DocumentResponse(
            id=str(doc.id),
            doc_type=doc.doc_type,
            title=doc.title,
            source_url=doc.source_url,
            metadata=doc.metadata,
            created_at=doc.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )


@router.get("/documents/count", response_model=DocumentCountResponse)
async def get_document_count(
    db: Session = Depends(get_db),
) -> DocumentCountResponse:
    """
    Get document counts by type.

    Returns statistics about ingested documents.

    Args:
        db: Database session

    Returns:
        Document counts by type

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        ingestor = DocumentIngestor(db)
        counts = ingestor.get_document_count()

        return DocumentCountResponse(
            counts=counts,
            total=sum(counts.values()),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document count: {str(e)}",
        )


@router.post("/documents/bulk-ingest", response_model=BulkIngestResponse)
async def bulk_ingest_sessions(
    request: BulkIngestRequest,
    db: Session = Depends(get_db),
) -> BulkIngestResponse:
    """
    Bulk ingest recent F1 sessions as documents.

    Automatically creates searchable documents from recent race sessions.

    Args:
        request: Bulk ingest parameters
        db: Database session

    Returns:
        Ingestion results

    Raises:
        HTTPException: If ingestion fails
    """
    try:
        ingestor = DocumentIngestor(db)
        documents = ingestor.bulk_ingest_sessions(limit=request.limit)

        return BulkIngestResponse(
            ingested_count=len(documents),
            document_ids=[str(doc.id) for doc in documents],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk ingest: {str(e)}",
        )
