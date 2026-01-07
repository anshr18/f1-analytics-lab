"""
OpenF1 API Client

Client for fetching real-time F1 data from the OpenF1 API.
Documentation: https://openf1.org/
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger


class OpenF1Client:
    """Client for OpenF1 API real-time data."""

    BASE_URL = "https://api.openf1.org/v1"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self._session_key: Optional[str] = None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_latest_session(self) -> Optional[Dict[str, Any]]:
        """Get the latest live F1 session."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/sessions", params={"session_type": "Race"})
            response.raise_for_status()
            sessions = response.json()

            if not sessions:
                return None

            # Get the most recent session
            latest = max(sessions, key=lambda s: s.get("date_start", ""))
            return latest

        except Exception as e:
            logger.error(f"Error fetching latest session: {e}")
            return None

    async def get_session_info(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/sessions/{session_key}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching session info for {session_key}: {e}")
            return None

    async def get_live_timing(self, session_key: str) -> List[Dict[str, Any]]:
        """Get current live timing data for all drivers."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/position",
                params={"session_key": session_key},
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching live timing: {e}")
            return []

    async def get_driver_position(self, session_key: str, driver_number: int) -> Optional[Dict[str, Any]]:
        """Get specific driver's current position data."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/position",
                params={"session_key": session_key, "driver_number": driver_number},
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None

        except Exception as e:
            logger.error(f"Error fetching driver {driver_number} position: {e}")
            return None

    async def get_lap_data(self, session_key: str, driver_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get lap time data."""
        try:
            params = {"session_key": session_key}
            if driver_number:
                params["driver_number"] = driver_number

            response = await self.client.get(f"{self.BASE_URL}/laps", params=params)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching lap data: {e}")
            return []

    async def get_pit_stops(self, session_key: str) -> List[Dict[str, Any]]:
        """Get pit stop data."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/pit", params={"session_key": session_key})
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching pit stops: {e}")
            return []

    async def get_race_control_messages(self, session_key: str) -> List[Dict[str, Any]]:
        """Get race control messages (flags, incidents, etc.)."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/race_control", params={"session_key": session_key})
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching race control messages: {e}")
            return []

    async def get_session_status(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get current session status."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/session_info", params={"session_key": session_key})
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None

        except Exception as e:
            logger.error(f"Error fetching session status: {e}")
            return None

    async def get_weather(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get current weather data."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/weather", params={"session_key": session_key})
            response.raise_for_status()
            data = response.json()
            return data[-1] if data else None  # Get latest weather

        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None

    async def stream_session(self, session_key: str, interval: float = 1.0):
        """
        Stream live session data at regular intervals.

        Args:
            session_key: OpenF1 session key
            interval: Update interval in seconds (default 1.0)

        Yields:
            Dict containing live timing, pit stops, race control, and session status
        """
        self._session_key = session_key
        logger.info(f"Starting live stream for session {session_key}")

        while True:
            try:
                # Fetch all live data in parallel
                timing_task = self.get_live_timing(session_key)
                pit_task = self.get_pit_stops(session_key)
                rc_task = self.get_race_control_messages(session_key)
                status_task = self.get_session_status(session_key)
                weather_task = self.get_weather(session_key)

                timing, pit_stops, race_control, status, weather = await asyncio.gather(
                    timing_task, pit_task, rc_task, status_task, weather_task, return_exceptions=True
                )

                yield {
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_key": session_key,
                    "timing": timing if not isinstance(timing, Exception) else [],
                    "pit_stops": pit_stops if not isinstance(pit_stops, Exception) else [],
                    "race_control": race_control if not isinstance(race_control, Exception) else [],
                    "session_status": status if not isinstance(status, Exception) else None,
                    "weather": weather if not isinstance(weather, Exception) else None,
                }

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Error in stream: {e}")
                await asyncio.sleep(interval)
