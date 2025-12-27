"""
F1 Intelligence Hub - Sessions API

Endpoints for F1 sessions (FP1, FP2, FP3, Q, Sprint, Race).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...core.errors import DataNotFoundError
from ...db.models.core import Session as DBSession
from ...db.models.timing import Lap, Stint
from ...schemas.sessions import SessionListResponse, SessionResponse

router = APIRouter()


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Sessions",
    description="Get list of sessions with optional filtering by event",
)
async def list_sessions(
    event_id: UUID = Query(None, description="Filter by event UUID"),
    is_ingested: bool = Query(None, description="Filter by ingestion status"),
    db: Session = Depends(get_db),
):
    """
    List sessions with optional filters.

    Args:
        event_id: Optional event UUID filter
        is_ingested: Optional ingestion status filter
        db: Database session

    Returns:
        List of sessions
    """
    query = db.query(DBSession)

    if event_id:
        query = query.filter(DBSession.event_id == event_id)

    if is_ingested is not None:
        query = query.filter(DBSession.is_ingested == is_ingested)

    sessions = query.order_by(DBSession.session_date.desc()).all()
    total = len(sessions)

    # Add lap/stint counts
    session_responses = []
    for session in sessions:
        lap_count = db.query(func.count(Lap.id)).filter(Lap.session_id == session.id).scalar()
        stint_count = db.query(func.count(Stint.id)).filter(Stint.session_id == session.id).scalar()

        session_data = SessionResponse.model_validate(session)
        session_data.lap_count = lap_count
        session_data.stint_count = stint_count
        session_responses.append(session_data)

    return SessionListResponse(total=total, sessions=session_responses)


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session",
    description="Get details for a specific session",
)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get session by ID.

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Session details

    Raises:
        404: Session not found
    """
    session = db.query(DBSession).filter(DBSession.id == session_id).first()

    if not session:
        raise DataNotFoundError(f"Session {session_id} not found")

    # Add lap/stint counts
    lap_count = db.query(func.count(Lap.id)).filter(Lap.session_id == session.id).scalar()
    stint_count = db.query(func.count(Stint.id)).filter(Stint.session_id == session.id).scalar()

    session_data = SessionResponse.model_validate(session)
    session_data.lap_count = lap_count
    session_data.stint_count = stint_count

    return session_data
