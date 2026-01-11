"""
Live Streaming API Endpoints

FastAPI endpoints for live F1 data streaming.
WebSocket functionality will be added later.
"""

from typing import Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from ...core.dependencies import get_db
from ...db.models import LiveEvent, LiveSession, LiveTiming, Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/live", tags=["live"])


@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
def start_live_session(
    session_id: UUID,
    openf1_session_key: str,
    db: DBSession = Depends(get_db),
):
    """
    Start a live streaming session.

    Args:
        session_id: F1Hub session UUID
        openf1_session_key: OpenF1 API session key

    Returns:
        LiveSession: Created live session
    """
    # Verify session exists
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if live session already exists
    existing = db.query(LiveSession).filter(
        LiveSession.session_id == session_id,
        LiveSession.is_active == True
    ).first()

    if existing:
        return {
            "id": str(existing.id),
            "session_id": str(existing.session_id),
            "is_active": existing.is_active,
            "openf1_session_key": existing.openf1_session_key,
            "current_lap": existing.current_lap,
            "session_status": existing.session_status,
            "track_status": existing.track_status,
        }

    # Create new live session
    live_session = LiveSession(
        session_id=session_id,
        openf1_session_key=openf1_session_key,
        is_active=True,
        session_status="Started",
        track_status="Unknown",
    )

    db.add(live_session)
    db.commit()
    db.refresh(live_session)

    logger.info(f"Started live session {live_session.id} for session {session_id}")

    return {
        "id": str(live_session.id),
        "session_id": str(live_session.session_id),
        "is_active": live_session.is_active,
        "openf1_session_key": live_session.openf1_session_key,
        "current_lap": live_session.current_lap,
        "session_status": live_session.session_status,
        "track_status": live_session.track_status,
    }


@router.post("/sessions/{live_session_id}/stop")
def stop_live_session(
    live_session_id: UUID,
    db: DBSession = Depends(get_db),
):
    """
    Stop a live streaming session.

    Args:
        live_session_id: LiveSession UUID

    Returns:
        Success message
    """
    live_session = db.query(LiveSession).filter(LiveSession.id == live_session_id).first()
    if not live_session:
        raise HTTPException(status_code=404, detail="Live session not found")

    live_session.is_active = False
    live_session.ended_at = None  # Will be set by database default
    db.commit()

    logger.info(f"Stopped live session {live_session_id}")

    return {"message": "Live session stopped", "live_session_id": str(live_session_id)}


@router.get("/sessions/active")
def get_active_sessions(db: DBSession = Depends(get_db)):
    """
    Get all active live sessions.

    Returns:
        List of active LiveSession records
    """
    sessions = db.query(LiveSession).filter(LiveSession.is_active == True).all()

    return [
        {
            "id": str(session.id),
            "session_id": str(session.session_id),
            "is_active": session.is_active,
            "openf1_session_key": session.openf1_session_key,
            "current_lap": session.current_lap,
            "session_status": session.session_status,
            "track_status": session.track_status,
            "started_at": session.created_at.isoformat() if session.created_at else None,
        }
        for session in sessions
    ]


@router.get("/sessions/{live_session_id}/timing")
def get_live_timing(
    live_session_id: UUID,
    limit: int = 100,
    db: DBSession = Depends(get_db),
):
    """
    Get recent timing data for a live session.

    Args:
        live_session_id: LiveSession UUID
        limit: Maximum number of records to return

    Returns:
        List of LiveTiming records
    """
    timing_data = (
        db.query(LiveTiming)
        .filter(LiveTiming.live_session_id == live_session_id)
        .order_by(LiveTiming.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "driver_number": t.driver_number,
            "lap_number": t.lap_number,
            "position": t.position,
            "gap_to_leader": t.gap_to_leader,
            "interval": t.interval,
            "last_lap_time": t.last_lap_time,
            "sector1_time": t.sector1_time,
            "sector2_time": t.sector2_time,
            "sector3_time": t.sector3_time,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
        }
        for t in timing_data
    ]


@router.get("/sessions/{live_session_id}/events")
def get_live_events(
    live_session_id: UUID,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: DBSession = Depends(get_db),
):
    """
    Get events for a live session.

    Args:
        live_session_id: LiveSession UUID
        event_type: Filter by event type (pit_stop, race_control, etc.)
        limit: Maximum number of records to return

    Returns:
        List of LiveEvent records
    """
    query = db.query(LiveEvent).filter(LiveEvent.live_session_id == live_session_id)

    if event_type:
        query = query.filter(LiveEvent.event_type == event_type)

    events = query.order_by(LiveEvent.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "driver_number": e.driver_number,
            "lap_number": e.lap_number,
            "description": e.description,
            "severity": e.severity,
            "data": e.data,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]
