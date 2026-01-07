"""
Live Timing Service

Orchestrates live F1 data streaming from OpenF1 API to WebSocket clients.
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from f1hub.db.models import LiveEvent, LiveSession, LiveTiming
from f1hub.services.live.openf1_client import OpenF1Client
from f1hub.services.live.websocket_manager import WebSocketManager


class LiveTimingService:
    """Service for processing and broadcasting live F1 timing data."""

    def __init__(self, db_session: AsyncSession, websocket_manager: WebSocketManager):
        self.db = db_session
        self.ws_manager = websocket_manager
        self.openf1_client = OpenF1Client()
        self._active_streams: Dict[str, asyncio.Task] = {}

    async def close(self):
        """Clean up resources."""
        # Cancel all active streams
        for task in self._active_streams.values():
            task.cancel()

        await self.openf1_client.close()
        logger.info("LiveTimingService closed")

    async def start_live_session(self, session_id: UUID, openf1_session_key: str) -> LiveSession:
        """
        Start a new live streaming session.

        Args:
            session_id: F1Hub session UUID
            openf1_session_key: OpenF1 API session key

        Returns:
            LiveSession: Created live session record
        """
        # Check if session is already live
        stmt = select(LiveSession).where(LiveSession.session_id == session_id, LiveSession.is_active == True)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"Live session already active for session {session_id}")
            return existing

        # Get initial session info from OpenF1
        session_info = await self.openf1_client.get_session_info(openf1_session_key)

        # Create live session record
        live_session = LiveSession(
            session_id=session_id,
            is_active=True,
            openf1_session_key=openf1_session_key,
            current_lap=0,
            session_status="Starting",
            track_status="Unknown",
        )

        self.db.add(live_session)
        await self.db.commit()
        await self.db.refresh(live_session)

        logger.info(f"Started live session {live_session.id} for session {session_id}")

        # Start streaming task
        stream_task = asyncio.create_task(self._stream_session_data(live_session))
        self._active_streams[str(live_session.id)] = stream_task

        return live_session

    async def stop_live_session(self, live_session_id: UUID):
        """Stop a live streaming session."""
        # Get live session
        live_session = await self.db.get(LiveSession, live_session_id)
        if not live_session:
            logger.warning(f"Live session {live_session_id} not found")
            return

        # Mark as inactive
        live_session.is_active = False
        live_session.ended_at = datetime.utcnow()
        await self.db.commit()

        # Cancel streaming task
        if str(live_session_id) in self._active_streams:
            self._active_streams[str(live_session_id)].cancel()
            del self._active_streams[str(live_session_id)]

        logger.info(f"Stopped live session {live_session_id}")

    async def _stream_session_data(self, live_session: LiveSession):
        """
        Main streaming loop for a live session.

        Args:
            live_session: LiveSession database record
        """
        session_key = live_session.openf1_session_key
        session_id = str(live_session.session_id)

        logger.info(f"Starting stream for session {session_id} (OpenF1: {session_key})")

        try:
            async for data in self.openf1_client.stream_session(session_key, interval=1.0):
                if not live_session.is_active:
                    logger.info(f"Session {session_id} no longer active, stopping stream")
                    break

                # Process and broadcast timing data
                await self._process_timing_data(live_session, data["timing"])

                # Process pit stops
                await self._process_pit_stops(live_session, data["pit_stops"])

                # Process race control messages
                await self._process_race_control(live_session, data["race_control"])

                # Update session status
                await self._update_session_status(live_session, data.get("session_status"))

                # Broadcast to WebSocket clients
                await self.ws_manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "live_update",
                        "data": {
                            "timing": data["timing"],
                            "pit_stops": data["pit_stops"],
                            "race_control": data["race_control"],
                            "session_status": data.get("session_status"),
                            "weather": data.get("weather"),
                        },
                    },
                )

        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in stream for session {session_id}: {e}")
            # Mark session as inactive on error
            live_session.is_active = False
            await self.db.commit()

    async def _process_timing_data(self, live_session: LiveSession, timing_data: list):
        """Process and store live timing data."""
        if not timing_data:
            return

        for position_data in timing_data:
            # Create or update timing record
            timing = LiveTiming(
                live_session_id=live_session.id,
                driver_number=position_data.get("driver_number"),
                lap_number=position_data.get("lap_number"),
                position=position_data.get("position"),
                gap_to_leader=position_data.get("gap_to_leader"),
                interval=position_data.get("interval"),
                last_lap_time=position_data.get("last_lap_time"),
                sector1_time=position_data.get("sector1_time"),
                sector2_time=position_data.get("sector2_time"),
                sector3_time=position_data.get("sector3_time"),
            )

            self.db.add(timing)

        await self.db.commit()

    async def _process_pit_stops(self, live_session: LiveSession, pit_stops: list):
        """Process and store pit stop events."""
        for pit_data in pit_stops:
            # Check if event already exists
            existing_event = await self.db.execute(
                select(LiveEvent).where(
                    LiveEvent.live_session_id == live_session.id,
                    LiveEvent.event_type == "pit_stop",
                    LiveEvent.driver_number == pit_data.get("driver_number"),
                    LiveEvent.lap_number == pit_data.get("lap_number"),
                )
            )

            if existing_event.scalar_one_or_none():
                continue

            # Create pit stop event
            event = LiveEvent(
                live_session_id=live_session.id,
                event_type="pit_stop",
                driver_number=pit_data.get("driver_number"),
                lap_number=pit_data.get("lap_number"),
                message=f"Pit stop - {pit_data.get('pit_duration', 0):.2f}s",
                data=pit_data,
            )

            self.db.add(event)

        await self.db.commit()

    async def _process_race_control(self, live_session: LiveSession, race_control: list):
        """Process and store race control messages."""
        for rc_data in race_control:
            # Check if event already exists
            existing_event = await self.db.execute(
                select(LiveEvent).where(
                    LiveEvent.live_session_id == live_session.id,
                    LiveEvent.event_type == "race_control",
                    LiveEvent.message == rc_data.get("message"),
                )
            )

            if existing_event.scalar_one_or_none():
                continue

            # Create race control event
            event = LiveEvent(
                live_session_id=live_session.id,
                event_type="race_control",
                message=rc_data.get("message"),
                flag=rc_data.get("flag"),
                data=rc_data,
            )

            self.db.add(event)

        await self.db.commit()

    async def _update_session_status(self, live_session: LiveSession, status_data: Optional[Dict]):
        """Update live session status."""
        if not status_data:
            return

        live_session.session_status = status_data.get("status", live_session.session_status)
        live_session.track_status = status_data.get("track_status", live_session.track_status)

        if "current_lap" in status_data:
            live_session.current_lap = status_data["current_lap"]

        await self.db.commit()

    async def get_active_sessions(self) -> list[LiveSession]:
        """Get all active live sessions."""
        stmt = select(LiveSession).where(LiveSession.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all()
