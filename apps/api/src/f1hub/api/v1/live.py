"""
Live Streaming API Endpoints

FastAPI endpoints for live F1 data streaming via WebSockets.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from f1hub.db.dependencies import get_db_session
from f1hub.db.models import LiveEvent, LiveSession, LiveTiming, Session
from f1hub.services.live import LiveTimingService, WebSocketManager

router = APIRouter(prefix="/live", tags=["live"])

# Global WebSocket manager instance
ws_manager: Optional[WebSocketManager] = None


async def get_ws_manager() -> WebSocketManager:
    """Dependency to get WebSocket manager."""
    global ws_manager
    if ws_manager is None:
        ws_manager = WebSocketManager()
        await ws_manager.initialize()
    return ws_manager


@router.on_event("startup")
async def startup_event():
    """Initialize WebSocket manager on startup."""
    global ws_manager
    ws_manager = WebSocketManager()
    await ws_manager.initialize()
    logger.info("WebSocket manager initialized")


@router.on_event("shutdown")
async def shutdown_event():
    """Close WebSocket manager on shutdown."""
    global ws_manager
    if ws_manager:
        await ws_manager.close()
    logger.info("WebSocket manager closed")


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    WebSocket endpoint for live timing updates.

    Args:
        session_id: F1Hub session UUID to subscribe to
    """
    await websocket.accept()
    connection_id = None

    try:
        # Verify session exists
        session = await db.get(Session, session_id)
        if not session:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            await websocket.close()
            return

        # Register connection
        manager = await get_ws_manager()
        connection_id = await manager.register(websocket, str(session_id))

        logger.info(f"WebSocket connected: {connection_id} for session {session_id}")

        # Send initial connection success message
        await websocket.send_json(
            {
                "type": "connected",
                "connection_id": connection_id,
                "session_id": str(session_id),
                "message": "Connected to live timing",
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle ping/pong
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if connection_id:
            manager = await get_ws_manager()
            await manager.unregister(connection_id, str(session_id))


@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_live_session(
    session_id: UUID,
    openf1_session_key: str,
    db: AsyncSession = Depends(get_db_session),
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
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create live timing service
    manager = await get_ws_manager()
    live_service = LiveTimingService(db, manager)

    try:
        live_session = await live_service.start_live_session(session_id, openf1_session_key)
        return {
            "id": str(live_session.id),
            "session_id": str(live_session.session_id),
            "is_active": live_session.is_active,
            "openf1_session_key": live_session.openf1_session_key,
            "current_lap": live_session.current_lap,
            "session_status": live_session.session_status,
            "track_status": live_session.track_status,
        }
    except Exception as e:
        logger.error(f"Error starting live session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{live_session_id}/stop")
async def stop_live_session(
    live_session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Stop a live streaming session.

    Args:
        live_session_id: LiveSession UUID

    Returns:
        Success message
    """
    manager = await get_ws_manager()
    live_service = LiveTimingService(db, manager)

    try:
        await live_service.stop_live_session(live_session_id)
        return {"message": "Live session stopped", "live_session_id": str(live_session_id)}
    except Exception as e:
        logger.error(f"Error stopping live session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active")
async def get_active_sessions(db: AsyncSession = Depends(get_db_session)):
    """
    Get all active live sessions.

    Returns:
        List of active LiveSession records
    """
    stmt = select(LiveSession).where(LiveSession.is_active == True)
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    return [
        {
            "id": str(session.id),
            "session_id": str(session.session_id),
            "is_active": session.is_active,
            "openf1_session_key": session.openf1_session_key,
            "current_lap": session.current_lap,
            "session_status": session.session_status,
            "track_status": session.track_status,
            "started_at": session.created_at.isoformat(),
        }
        for session in sessions
    ]


@router.get("/sessions/{live_session_id}/timing")
async def get_live_timing(
    live_session_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get recent timing data for a live session.

    Args:
        live_session_id: LiveSession UUID
        limit: Maximum number of records to return

    Returns:
        List of LiveTiming records
    """
    stmt = (
        select(LiveTiming)
        .where(LiveTiming.live_session_id == live_session_id)
        .order_by(LiveTiming.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    timing_data = result.scalars().all()

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
            "timestamp": t.created_at.isoformat(),
        }
        for t in timing_data
    ]


@router.get("/sessions/{live_session_id}/events")
async def get_live_events(
    live_session_id: UUID,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
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
    stmt = select(LiveEvent).where(LiveEvent.live_session_id == live_session_id)

    if event_type:
        stmt = stmt.where(LiveEvent.event_type == event_type)

    stmt = stmt.order_by(LiveEvent.created_at.desc()).limit(limit)

    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "driver_number": e.driver_number,
            "lap_number": e.lap_number,
            "message": e.message,
            "flag": e.flag,
            "data": e.data,
            "timestamp": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.get("/connections/count")
async def get_connection_count(session_id: Optional[UUID] = None):
    """
    Get the number of active WebSocket connections.

    Args:
        session_id: Optional session ID to count connections for

    Returns:
        Connection count
    """
    manager = await get_ws_manager()
    count = await manager.get_connection_count(str(session_id) if session_id else None)
    return {"count": count, "session_id": str(session_id) if session_id else None}
