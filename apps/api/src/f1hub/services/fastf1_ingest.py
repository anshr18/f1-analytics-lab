"""
F1 Intelligence Hub - FastF1 Ingestion Service

Service for ingesting F1 data from FastF1 into the database.
"""

import logging
from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from f1data.clients import FastF1Client
from f1data.parsers import FastF1Parser

from ..core.config import get_settings
from ..db.models.core import Driver, Event, Season
from ..db.models.core import Session as DBSession
from ..db.models.timing import Lap, Stint
from ..db.models.track_status import RaceControl

logger = logging.getLogger(__name__)
settings = get_settings()


class FastF1IngestService:
    """
    Service for ingesting F1 data from FastF1.

    Handles the complete ingestion pipeline:
    1. Get or create Event and Session
    2. Load data from FastF1
    3. Parse data
    4. Insert into database
    5. Mark session as ingested
    """

    def __init__(self, db: Session):
        """
        Initialize ingestion service.

        Args:
            db: Database session
        """
        self.db = db
        self.client = FastF1Client(cache_dir=settings.FASTF1_CACHE_DIR)
        self.parser = FastF1Parser()

    def ingest_session(self, year: int, round_number: int, session_type: str) -> UUID:
        """
        Ingest a complete F1 session.

        Args:
            year: Season year
            round_number: Round number
            session_type: Session type (FP1, FP2, FP3, Q, Sprint, Race)

        Returns:
            Session UUID

        Raises:
            ValueError: If ingestion fails
        """
        logger.info(f"Starting ingestion: {year} Round {round_number} {session_type}")

        try:
            # Step 1: Load FastF1 session
            ff1_session = self.client.get_session(year, round_number, session_type)
            ff1_session = self.client.load_session(ff1_session, laps=True, telemetry=False, messages=True)

            # Step 2: Parse session metadata
            session_data = self.parser.parse_session(ff1_session)

            # Step 3: Get or create Season
            season = self._get_or_create_season(session_data["season_year"])

            # Step 4: Get or create Event
            event = self._get_or_create_event(session_data)

            # Step 5: Get or create Session
            db_session = self._get_or_create_session(event.id, session_data)

            # Check if already ingested
            if db_session.is_ingested:
                logger.warning(f"Session {db_session.id} already ingested, skipping")
                return db_session.id

            # Step 6: Get or create Drivers
            self._get_or_create_drivers(ff1_session)

            # Step 7: Parse and insert Stints (must be before laps for FK)
            stints_data = self.parser.parse_stints(ff1_session)
            stint_map = self._insert_stints(db_session.id, stints_data)

            # Step 8: Parse and insert Laps
            laps_data = self.parser.parse_laps(ff1_session)
            self._insert_laps(db_session.id, laps_data, stint_map)

            # Step 9: Parse and insert Race Control messages
            rc_data = self.parser.parse_race_control(ff1_session)
            self._insert_race_control(db_session.id, rc_data)

            # Step 10: Mark session as ingested
            db_session.is_ingested = True
            db_session.source = "fastf1"
            self.db.commit()

            logger.info(
                f"Ingestion complete: Session {db_session.id}, "
                f"{len(laps_data)} laps, {len(stints_data)} stints, {len(rc_data)} messages"
            )

            return db_session.id

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            raise ValueError(f"Failed to ingest session: {e}") from e

    def _get_or_create_season(self, year: int) -> Season:
        """Get or create season."""
        season = self.db.query(Season).filter(Season.year == year).first()

        if not season:
            season = Season(year=year)
            self.db.add(season)
            self.db.flush()
            logger.info(f"Created season {year}")

        return season

    def _get_or_create_event(self, session_data: dict) -> Event:
        """Get or create event."""
        event = (
            self.db.query(Event)
            .filter(
                Event.season_year == session_data["season_year"],
                Event.round_number == session_data["round_number"],
            )
            .first()
        )

        if not event:
            event = Event(
                season_year=session_data["season_year"],
                round_number=session_data["round_number"],
                event_name=session_data["event_name"],
                country=session_data["country"],
                location=session_data["location"],
                event_date=session_data["event_date"],
            )
            self.db.add(event)
            self.db.flush()
            logger.info(f"Created event: {event.event_name}")

        return event

    def _get_or_create_session(self, event_id: UUID, session_data: dict) -> DBSession:
        """Get or create session."""
        db_session = (
            self.db.query(DBSession)
            .filter(
                DBSession.event_id == event_id,
                DBSession.session_type == session_data["session_type"],
            )
            .first()
        )

        if not db_session:
            db_session = DBSession(
                event_id=event_id,
                session_type=session_data["session_type"],
                session_date=session_data["session_date"],
                is_ingested=False,
            )
            self.db.add(db_session)
            self.db.flush()
            logger.info(f"Created session: {session_data['session_type']}")

        return db_session

    def _get_or_create_drivers(self, ff1_session) -> None:
        """Get or create drivers from session."""
        import pandas as pd

        for driver_code in ff1_session.drivers:
            try:
                # Get driver info from FastF1 (returns pandas Series)
                driver_info = ff1_session.get_driver(driver_code)

                # Extract values from Series - use .get() method or check with pd.notna()
                abbreviation = str(driver_info.get("Abbreviation", driver_code)) if pd.notna(driver_info.get("Abbreviation")) else str(driver_code)[:3].upper()

                # Use abbreviation (3-letter code) as driver_id in lowercase
                driver_id = abbreviation.lower()

                # Check if driver already exists
                existing = self.db.query(Driver).filter(Driver.driver_id == driver_id).first()

                if not existing:
                    full_name = str(driver_info.get("FullName", driver_code)) if pd.notna(driver_info.get("FullName")) else str(driver_code)

                    # Handle driver number - could be NaN
                    driver_num = driver_info.get("DriverNumber")
                    driver_number = int(driver_num) if pd.notna(driver_num) else None

                    driver = Driver(
                        driver_id=driver_id,
                        full_name=full_name,
                        abbreviation=abbreviation,
                        number=driver_number,
                        country=None,  # Not available in FastF1
                    )
                    self.db.add(driver)
                    logger.info(f"Added driver: {driver_id} = {full_name} #{driver_number}")

            except Exception as e:
                logger.error(f"Failed to add driver {driver_code}: {e}")
                raise

        self.db.flush()
        logger.info(f"Processed {len(ff1_session.drivers)} drivers")

    def _insert_stints(self, session_id: UUID, stints_data: list) -> dict:
        """
        Insert stints and return mapping of (driver_id, stint_number) -> stint_id.

        This mapping is needed to associate laps with their stints.
        """
        stint_map = {}

        for stint_data in stints_data:
            stint = Stint(
                session_id=session_id,
                driver_id=stint_data["driver_id"],
                stint_number=stint_data["stint_number"],
                compound=stint_data["compound"],
                lap_start=stint_data["lap_start"],
                lap_end=stint_data["lap_end"],
                total_laps=stint_data["total_laps"],
            )
            self.db.add(stint)
            self.db.flush()

            # Map (driver, stint_number) -> stint_id
            key = (stint_data["driver_id"], stint_data["stint_number"])
            stint_map[key] = stint.id

        logger.info(f"Inserted {len(stints_data)} stints")
        return stint_map

    def _insert_laps(self, session_id: UUID, laps_data: list, stint_map: dict) -> None:
        """Insert laps with stint associations."""
        for lap_data in laps_data:
            # Find stint for this lap
            driver_id = lap_data["driver_id"]
            lap_number = lap_data["lap_number"]
            stint_id = self._find_stint_for_lap(driver_id, lap_number, stint_map)

            lap = Lap(
                session_id=session_id,
                driver_id=driver_id,
                lap_number=lap_number,
                lap_time=lap_data.get("lap_time"),
                sector_1_time=lap_data.get("sector_1_time"),
                sector_2_time=lap_data.get("sector_2_time"),
                sector_3_time=lap_data.get("sector_3_time"),
                compound=lap_data.get("compound"),
                tyre_life=lap_data.get("tyre_life"),
                stint_id=stint_id,
                track_status=lap_data.get("track_status"),
                is_personal_best=lap_data.get("is_personal_best", False),
                position=lap_data.get("position"),
                deleted=lap_data.get("deleted", False),
                is_pit_out_lap=lap_data.get("is_pit_out_lap", False),
                is_pit_in_lap=lap_data.get("is_pit_in_lap", False),
            )
            self.db.add(lap)

        self.db.flush()
        logger.info(f"Inserted {len(laps_data)} laps")

    def _find_stint_for_lap(self, driver_id: str, lap_number: int, stint_map: dict) -> Optional[UUID]:
        """Find stint ID for a lap based on lap number."""
        # Find the stint where lap_start <= lap_number <= lap_end
        for (stint_driver, stint_num), stint_id in stint_map.items():
            if stint_driver == driver_id:
                # Get stint from DB to check lap range
                stint = self.db.query(Stint).filter(Stint.id == stint_id).first()
                if stint and stint.lap_start <= lap_number <= (stint.lap_end or float("inf")):
                    return stint_id
        return None

    def _insert_race_control(self, session_id: UUID, rc_data: list) -> None:
        """Insert race control messages."""
        for msg_data in rc_data:
            message = RaceControl(
                session_id=session_id,
                timestamp=msg_data["timestamp"],
                category=msg_data["category"],
                message=msg_data["message"],
                flag=msg_data.get("flag"),
                scope=msg_data.get("scope"),
            )
            self.db.add(message)

        self.db.flush()
        logger.info(f"Inserted {len(rc_data)} race control messages")
