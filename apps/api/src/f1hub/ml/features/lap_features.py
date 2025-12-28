"""
Lap Feature Computation

Calculates lap-level features including time deltas and encodings.
"""

import logging
from typing import Dict, List
from uuid import UUID

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from f1hub.db.models.features import LapFeature
from f1hub.db.models.timing import Lap, Stint

logger = logging.getLogger(__name__)


# Encoding mappings
COMPOUND_CODES = {
    "SOFT": 1,
    "MEDIUM": 2,
    "HARD": 3,
    "INTERMEDIATE": 4,
    "WET": 5,
}

TRACK_STATUS_CODES = {
    "1": 1,  # Green
    "2": 2,  # Yellow
    "3": 3,  # Safety Car
    "4": 4,  # VSC
    "5": 5,  # Red flag
}


def compute_lap_features(session_id: UUID, db: Session) -> int:
    """
    Compute and insert lap-level features for a session.

    Features:
    - delta_to_leader: Time gap to session leader (seconds)
    - delta_to_ahead: Time gap to car ahead (seconds)
    - delta_to_personal_best: Gap to driver's best lap (seconds)
    - tyre_age: Laps completed on current tyre (from stint)
    - compound_code: SOFT=1, MEDIUM=2, HARD=3, INT=4, WET=5
    - track_status_code: Green=1, Yellow=2, SC=3, VSC=4, Red=5
    - positions_gained: Position change from lap 1 to current lap

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Number of features inserted
    """
    # Check if features already exist
    existing_count = (
        db.query(LapFeature)
        .join(Lap)
        .filter(Lap.session_id == session_id)
        .count()
    )

    if existing_count > 0:
        logger.info(f"Lap features already exist for session {session_id}, skipping")
        return 0

    # Fetch all laps for this session with their stint information
    laps_query = (
        db.query(Lap, Stint)
        .join(Stint, Lap.stint_id == Stint.id, isouter=True)
        .filter(Lap.session_id == session_id, Lap.deleted == False)  # noqa: E712
        .order_by(Lap.lap_number, Lap.position)
        .all()
    )

    if not laps_query:
        logger.warning(f"No laps found for session {session_id}")
        return 0

    # Convert to pandas for easier manipulation
    lap_data = []
    for lap, stint in laps_query:
        lap_data.append(
            {
                "lap_id": lap.id,
                "driver_id": lap.driver_id,
                "lap_number": lap.lap_number,
                "lap_time": lap.lap_time.total_seconds() if lap.lap_time else None,
                "position": lap.position,
                "track_status": lap.track_status,
                "compound": stint.compound if stint else None,
                "stint_id": stint.id if stint else None,
                "stint_lap_start": stint.lap_start if stint else None,
            }
        )

    df = pd.DataFrame(lap_data)

    logger.info(f"Computing features for {len(df)} laps")

    # Calculate cumulative time for each driver (for delta calculations)
    df["cumulative_time"] = df.groupby("driver_id")["lap_time"].transform("cumsum")

    # For each lap, calculate features
    features_to_insert: List[LapFeature] = []

    for lap_num in sorted(df["lap_number"].unique()):
        lap_df = df[df["lap_number"] == lap_num].copy()

        # Sort by cumulative time to get positions
        lap_df = lap_df.sort_values("cumulative_time")
        lap_df["calculated_position"] = range(1, len(lap_df) + 1)

        # Leader's cumulative time
        leader_time = lap_df["cumulative_time"].min()

        for idx, row in lap_df.iterrows():
            # Delta to leader
            delta_to_leader = None
            if pd.notna(row["cumulative_time"]) and pd.notna(leader_time):
                delta_to_leader = float(row["cumulative_time"] - leader_time)

            # Delta to car ahead
            delta_to_ahead = None
            current_pos = row.get("calculated_position", row.get("position"))
            if current_pos and current_pos > 1:
                ahead_driver = lap_df[lap_df["calculated_position"] == current_pos - 1]
                if not ahead_driver.empty:
                    ahead_time = ahead_driver.iloc[0]["cumulative_time"]
                    if pd.notna(row["cumulative_time"]) and pd.notna(ahead_time):
                        delta_to_ahead = float(row["cumulative_time"] - ahead_time)

            # Delta to personal best
            delta_to_personal_best = None
            driver_laps = df[df["driver_id"] == row["driver_id"]]
            if not driver_laps.empty:
                personal_best = driver_laps["lap_time"].min()
                if pd.notna(row["lap_time"]) and pd.notna(personal_best):
                    delta_to_personal_best = float(row["lap_time"] - personal_best)

            # Tyre age (laps on current tyre)
            tyre_age = None
            if pd.notna(row["stint_lap_start"]):
                tyre_age = int(row["lap_number"] - row["stint_lap_start"] + 1)

            # Compound code
            compound_code = None
            if pd.notna(row["compound"]):
                compound_code = COMPOUND_CODES.get(row["compound"])

            # Track status code
            track_status_code = None
            if pd.notna(row["track_status"]):
                track_status_code = TRACK_STATUS_CODES.get(str(row["track_status"]), 1)

            # Positions gained (from lap 1)
            positions_gained = None
            if lap_num > 1:
                lap_1_data = df[(df["driver_id"] == row["driver_id"]) & (df["lap_number"] == 1)]
                if not lap_1_data.empty and pd.notna(row["position"]):
                    lap_1_pos = lap_1_data.iloc[0]["position"]
                    if pd.notna(lap_1_pos):
                        positions_gained = int(lap_1_pos - row["position"])

            # Create feature
            feature = LapFeature(
                lap_id=row["lap_id"],
                delta_to_leader=delta_to_leader,
                delta_to_ahead=delta_to_ahead,
                delta_to_personal_best=delta_to_personal_best,
                tyre_age=tyre_age,
                compound_code=compound_code,
                track_status_code=track_status_code,
                position=int(row["position"]) if pd.notna(row["position"]) else None,
                positions_gained=positions_gained,
                extra_features={
                    "driver_id": row["driver_id"],
                    "lap_number": int(row["lap_number"]),
                },
            )

            features_to_insert.append(feature)

    # Bulk insert
    if features_to_insert:
        db.bulk_save_objects(features_to_insert)
        db.flush()

    logger.info(f"Inserted {len(features_to_insert)} lap features")

    return len(features_to_insert)
