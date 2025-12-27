"""
F1 Data - FastF1 Client

Client for accessing F1 data via the FastF1 library.
"""

import logging
from pathlib import Path
from typing import Optional

import fastf1

logger = logging.getLogger(__name__)


class FastF1Client:
    """
    FastF1 client for loading F1 session data.

    Handles cache setup and session loading.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize FastF1 client.

        Args:
            cache_dir: Directory for FastF1 cache (defaults to ./data/fastf1_cache)
        """
        if cache_dir is None:
            cache_dir = str(Path.cwd() / "data" / "fastf1_cache")

        # Create cache directory if it doesn't exist
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        # Enable FastF1 cache
        fastf1.Cache.enable_cache(cache_dir)
        logger.info(f"FastF1 cache enabled at {cache_dir}")

        self.cache_dir = cache_dir

    def get_session(self, year: int, round_number: int, session_type: str) -> fastf1.core.Session:
        """
        Get F1 session object.

        Args:
            year: Season year
            round_number: Round number (1-24)
            session_type: Session type (FP1, FP2, FP3, Q, Sprint, Race)

        Returns:
            FastF1 Session object

        Raises:
            ValueError: If session cannot be loaded
        """
        try:
            logger.info(f"Loading session: {year} Round {round_number} {session_type}")
            session = fastf1.get_session(year, round_number, session_type)
            return session
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            raise ValueError(f"Could not load session {year} R{round_number} {session_type}") from e

    def load_session(
        self,
        session: fastf1.core.Session,
        laps: bool = True,
        telemetry: bool = False,
        weather: bool = False,
        messages: bool = True,
    ) -> fastf1.core.Session:
        """
        Load session data.

        Args:
            session: FastF1 Session object
            laps: Load lap data
            telemetry: Load telemetry data (slow, only for detailed analysis)
            weather: Load weather data
            messages: Load race control messages

        Returns:
            Loaded Session object

        Raises:
            ValueError: If session data cannot be loaded
        """
        try:
            logger.info(f"Loading session data: {session.event['EventName']} {session.name}")

            # Load data based on flags
            session.load(laps=laps, telemetry=telemetry, weather=weather, messages=messages)

            logger.info(
                f"Session loaded successfully: {len(session.laps)} laps, "
                f"{len(session.drivers) if hasattr(session, 'drivers') else 0} drivers"
            )

            return session
        except Exception as e:
            logger.error(f"Failed to load session data: {e}")
            raise ValueError(f"Could not load session data") from e

    def get_event_schedule(self, year: int) -> list:
        """
        Get event schedule for a season.

        Args:
            year: Season year

        Returns:
            List of events with metadata

        Raises:
            ValueError: If schedule cannot be loaded
        """
        try:
            logger.info(f"Loading event schedule for {year}")
            schedule = fastf1.get_event_schedule(year)
            return schedule.to_dict("records")
        except Exception as e:
            logger.error(f"Failed to load event schedule: {e}")
            raise ValueError(f"Could not load {year} schedule") from e
