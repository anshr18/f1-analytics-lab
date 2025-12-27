"""
F1 Data - FastF1 Parser

Parses FastF1 session data into normalized dictionaries for database ingestion.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import fastf1
import pandas as pd

logger = logging.getLogger(__name__)


class FastF1Parser:
    """
    Parser for FastF1 session data.

    Converts FastF1 objects to normalized dictionaries compatible with our database schema.
    """

    def parse_session(self, session: fastf1.core.Session) -> Dict[str, Any]:
        """
        Parse session metadata.

        Args:
            session: Loaded FastF1 Session object

        Returns:
            Session metadata dictionary
        """
        event = session.event

        return {
            "season_year": int(event["EventDate"].year),
            "round_number": int(event["RoundNumber"]),
            "event_name": str(event["EventName"]),
            "country": str(event["Country"]),
            "location": str(event["Location"]),
            "event_date": event["EventDate"].date(),
            "session_type": str(session.name),
            "session_date": session.date.date() if session.date else event["EventDate"].date(),
        }

    def parse_laps(self, session: fastf1.core.Session) -> List[Dict[str, Any]]:
        """
        Parse lap data from session.

        Args:
            session: Loaded FastF1 Session object

        Returns:
            List of lap dictionaries
        """
        if not hasattr(session, "laps") or session.laps is None or session.laps.empty:
            logger.warning("No lap data available in session")
            return []

        laps_data = []

        # Iterate through all laps
        for idx, lap in session.laps.iterrows():
            try:
                # Convert timedelta to Python timedelta (handle NaT/NaN)
                lap_time = self._convert_timedelta(lap.get("LapTime"))
                sector_1 = self._convert_timedelta(lap.get("Sector1Time"))
                sector_2 = self._convert_timedelta(lap.get("Sector2Time"))
                sector_3 = self._convert_timedelta(lap.get("Sector3Time"))

                # Get driver code
                driver_id = str(lap.get("Driver", "UNKNOWN")).lower().replace(" ", "_")

                lap_dict = {
                    "driver_id": driver_id,
                    "lap_number": int(lap.get("LapNumber", 0)),
                    "lap_time": lap_time,
                    "sector_1_time": sector_1,
                    "sector_2_time": sector_2,
                    "sector_3_time": sector_3,
                    "compound": str(lap.get("Compound", "")).upper() if pd.notna(lap.get("Compound")) else None,
                    "tyre_life": int(lap.get("TyreLife", 0)) if pd.notna(lap.get("TyreLife")) else None,
                    "track_status": self._parse_track_status(lap.get("TrackStatus")),
                    "is_personal_best": bool(lap.get("IsPersonalBest", False)),
                    "position": int(lap.get("Position", 0)) if pd.notna(lap.get("Position")) else None,
                    "deleted": bool(lap.get("Deleted", False)),
                    "is_pit_out_lap": bool(lap.get("PitOutTime", False) is not pd.NaT),
                    "is_pit_in_lap": bool(lap.get("PitInTime", False) is not pd.NaT),
                }

                laps_data.append(lap_dict)

            except Exception as e:
                logger.warning(f"Failed to parse lap {idx}: {e}")
                continue

        logger.info(f"Parsed {len(laps_data)} laps")
        return laps_data

    def parse_stints(self, session: fastf1.core.Session) -> List[Dict[str, Any]]:
        """
        Parse stint data from session.

        Identifies stints by grouping consecutive laps with the same compound.

        Args:
            session: Loaded FastF1 Session object

        Returns:
            List of stint dictionaries
        """
        if not hasattr(session, "laps") or session.laps is None or session.laps.empty:
            logger.warning("No lap data available for stint parsing")
            return []

        stints_data = []

        # Group laps by driver
        for driver in session.drivers:
            driver_laps = session.laps.pick_driver(driver)

            if driver_laps.empty:
                continue

            driver_id = str(driver).lower().replace(" ", "_")
            stint_number = 1
            current_compound = None
            stint_start = None

            for idx, lap in driver_laps.iterrows():
                compound = str(lap.get("Compound", "")).upper()

                # Skip laps without compound info
                if not compound or pd.isna(compound) or compound == "":
                    continue

                # New stint detected
                if compound != current_compound:
                    # Save previous stint if exists
                    if current_compound is not None and stint_start is not None:
                        stint_dict = {
                            "driver_id": driver_id,
                            "stint_number": stint_number,
                            "compound": current_compound,
                            "lap_start": int(stint_start),
                            "lap_end": int(lap.get("LapNumber", 0)) - 1,
                            "total_laps": int(lap.get("LapNumber", 0)) - int(stint_start),
                        }
                        stints_data.append(stint_dict)
                        stint_number += 1

                    # Start new stint
                    current_compound = compound
                    stint_start = int(lap.get("LapNumber", 0))

            # Save final stint
            if current_compound is not None and stint_start is not None:
                last_lap = int(driver_laps.iloc[-1].get("LapNumber", 0))
                stint_dict = {
                    "driver_id": driver_id,
                    "stint_number": stint_number,
                    "compound": current_compound,
                    "lap_start": int(stint_start),
                    "lap_end": last_lap,
                    "total_laps": last_lap - int(stint_start) + 1,
                }
                stints_data.append(stint_dict)

        logger.info(f"Parsed {len(stints_data)} stints")
        return stints_data

    def parse_race_control(self, session: fastf1.core.Session) -> List[Dict[str, Any]]:
        """
        Parse race control messages.

        Args:
            session: Loaded FastF1 Session object

        Returns:
            List of race control message dictionaries
        """
        if not hasattr(session, "race_control_messages") or session.race_control_messages is None:
            logger.warning("No race control messages available")
            return []

        messages_data = []

        for idx, msg in session.race_control_messages.iterrows():
            try:
                message_dict = {
                    "timestamp": pd.to_datetime(msg.get("Time")).to_pydatetime(),
                    "category": str(msg.get("Category", "UNKNOWN")),
                    "message": str(msg.get("Message", "")),
                    "flag": str(msg.get("Flag", "")).upper() if pd.notna(msg.get("Flag")) else None,
                    "scope": str(msg.get("Scope", "")).upper() if pd.notna(msg.get("Scope")) else None,
                }
                messages_data.append(message_dict)

            except Exception as e:
                logger.warning(f"Failed to parse race control message {idx}: {e}")
                continue

        logger.info(f"Parsed {len(messages_data)} race control messages")
        return messages_data

    # Helper methods

    def _convert_timedelta(self, td: Any) -> Optional[timedelta]:
        """
        Convert pandas Timedelta to Python timedelta.

        Args:
            td: Pandas Timedelta or NaT

        Returns:
            Python timedelta or None
        """
        if pd.isna(td):
            return None

        try:
            if isinstance(td, pd.Timedelta):
                return td.to_pytimedelta()
            elif isinstance(td, timedelta):
                return td
            else:
                return None
        except Exception:
            return None

    def _parse_track_status(self, status: Any) -> Optional[str]:
        """
        Parse track status code to string.

        Args:
            status: Track status code

        Returns:
            Track status string (Green, Yellow, SC, VSC, Red)
        """
        if pd.isna(status):
            return None

        status_map = {
            "1": "Green",
            "2": "Yellow",
            "3": "Green",  # All clear after yellow
            "4": "SC",  # Safety Car
            "5": "Red",
            "6": "VSC",  # Virtual Safety Car
            "7": "VSC",  # VSC Ending
        }

        return status_map.get(str(status), "Green")
