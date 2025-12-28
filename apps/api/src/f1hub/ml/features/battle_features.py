"""
Battle Feature Computation

Detects battles between drivers and labels overtakes for ML training.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from f1hub.db.models.features import BattleFeature
from f1hub.db.models.timing import Lap, Stint

logger = logging.getLogger(__name__)


# Battle detection threshold (seconds)
BATTLE_GAP_THRESHOLD = 2.0  # Cars within 2 seconds

# Overtake lookahead window (laps)
OVERTAKE_LOOKAHEAD = 3  # Check next 3 laps for position change

# Compound values for tyre advantage calculation
COMPOUND_VALUES = {"SOFT": 1, "MEDIUM": 2, "HARD": 3, "INTERMEDIATE": 4, "WET": 5}


def compute_battle_features(session_id: UUID, db: Session) -> int:
    """
    Detect battles and compute battle features for a session.

    Battle Definition: Two cars within 2 seconds for sustained period

    Features:
    - gap_seconds: Time gap between cars (seconds)
    - closing_rate: Gap change per lap (s/lap, negative = closing)
    - overtake_occurred: Binary (1 if overtake in next 3 laps)
    - overtake_within_laps: Laps until overtake (or NULL)
    - drs_available: 1 if gap < 1s and lap > 2 (approximation)
    - tyre_advantage: Compound difference (attacking car - defending car)

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Number of battle records inserted
    """
    # Check if features already exist
    existing_count = db.query(BattleFeature).filter(
        BattleFeature.session_id == session_id
    ).count()

    if existing_count > 0:
        logger.info(f"Battle features already exist for session {session_id}, skipping")
        return 0

    # Fetch all laps for this session with cumulative times
    laps_query = (
        db.query(Lap, Stint)
        .join(Stint, Lap.stint_id == Stint.id, isouter=True)
        .filter(
            Lap.session_id == session_id,
            Lap.deleted == False,  # noqa: E712
            Lap.lap_time != None,  # noqa: E711
        )
        .order_by(Lap.lap_number, Lap.position)
        .all()
    )

    if not laps_query:
        logger.warning(f"No laps found for session {session_id}")
        return 0

    # Build dataframe with cumulative times
    lap_data = []
    for lap, stint in laps_query:
        lap_data.append(
            {
                "driver_id": lap.driver_id,
                "lap_number": lap.lap_number,
                "lap_time": lap.lap_time.total_seconds(),
                "position": lap.position,
                "compound": stint.compound if stint else None,
            }
        )

    df = pd.DataFrame(lap_data)

    # Calculate cumulative time for each driver
    df = df.sort_values(["driver_id", "lap_number"])
    df["cumulative_time"] = df.groupby("driver_id")["lap_time"].cumsum()

    logger.info(f"Analyzing {len(df)} laps for battle detection")

    battles_to_insert: List[BattleFeature] = []

    # Process each lap
    for lap_num in sorted(df["lap_number"].unique()):
        lap_df = df[df["lap_number"] == lap_num].copy()

        # Sort by cumulative time (race order)
        lap_df = lap_df.sort_values("cumulative_time").reset_index(drop=True)

        # Check each adjacent pair of drivers
        for i in range(len(lap_df) - 1):
            driver_ahead = lap_df.iloc[i]
            driver_behind = lap_df.iloc[i + 1]

            # Calculate gap
            gap_seconds = float(
                driver_behind["cumulative_time"] - driver_ahead["cumulative_time"]
            )

            # Only process if within battle threshold
            if gap_seconds > BATTLE_GAP_THRESHOLD:
                continue

            # Calculate closing rate (gap change from previous lap)
            closing_rate = _calculate_closing_rate(
                df, lap_num, driver_ahead["driver_id"], driver_behind["driver_id"]
            )

            # Check for overtake in next N laps
            overtake_info = _check_overtake(
                df,
                lap_num,
                driver_ahead["driver_id"],
                driver_behind["driver_id"],
                lookahead=OVERTAKE_LOOKAHEAD,
            )

            # DRS available (approximation: gap < 1s and after lap 2)
            drs_available = 1 if gap_seconds < 1.0 and lap_num > 2 else 0

            # Tyre advantage (behind - ahead, positive = advantage to behind)
            tyre_advantage = _calculate_tyre_advantage(
                driver_behind["compound"], driver_ahead["compound"]
            )

            # Create battle feature
            battle = BattleFeature(
                session_id=session_id,
                lap_number=int(lap_num),
                driver_ahead_id=driver_ahead["driver_id"],
                driver_behind_id=driver_behind["driver_id"],
                gap_seconds=gap_seconds,
                closing_rate=closing_rate,
                overtake_occurred=overtake_info["occurred"],
                overtake_within_laps=overtake_info["within_laps"],
                drs_available=drs_available,
                tyre_advantage=tyre_advantage,
                extra_features={
                    "position_ahead": int(driver_ahead["position"])
                    if pd.notna(driver_ahead["position"])
                    else None,
                    "position_behind": int(driver_behind["position"])
                    if pd.notna(driver_behind["position"])
                    else None,
                    "compound_ahead": driver_ahead["compound"],
                    "compound_behind": driver_behind["compound"],
                },
            )

            battles_to_insert.append(battle)

    # Bulk insert
    if battles_to_insert:
        db.bulk_save_objects(battles_to_insert)
        db.flush()

    logger.info(f"Inserted {len(battles_to_insert)} battle features")

    # Count overtakes for logging
    overtake_count = sum(1 for b in battles_to_insert if b.overtake_occurred == 1)
    logger.info(f"Detected {overtake_count} overtakes")

    return len(battles_to_insert)


def _calculate_closing_rate(
    df: pd.DataFrame, lap_num: int, driver_ahead_id: str, driver_behind_id: str
) -> Optional[float]:
    """
    Calculate the rate at which the gap is changing (s/lap).

    Negative = gap is closing, positive = gap is increasing.
    """
    if lap_num == 1:
        return None  # No previous lap

    # Get current gap
    current_lap = df[df["lap_number"] == lap_num]
    ahead_current = current_lap[current_lap["driver_id"] == driver_ahead_id]
    behind_current = current_lap[current_lap["driver_id"] == driver_behind_id]

    if ahead_current.empty or behind_current.empty:
        return None

    current_gap = float(
        behind_current.iloc[0]["cumulative_time"] - ahead_current.iloc[0]["cumulative_time"]
    )

    # Get previous gap
    prev_lap = df[df["lap_number"] == lap_num - 1]
    ahead_prev = prev_lap[prev_lap["driver_id"] == driver_ahead_id]
    behind_prev = prev_lap[prev_lap["driver_id"] == driver_behind_id]

    if ahead_prev.empty or behind_prev.empty:
        return None

    prev_gap = float(
        behind_prev.iloc[0]["cumulative_time"] - ahead_prev.iloc[0]["cumulative_time"]
    )

    # Closing rate = change in gap (positive = opening up, negative = closing)
    closing_rate = current_gap - prev_gap

    return closing_rate


def _check_overtake(
    df: pd.DataFrame, lap_num: int, driver_ahead_id: str, driver_behind_id: str, lookahead: int
) -> Dict:
    """
    Check if driver_behind overtakes driver_ahead in the next N laps.

    Returns:
        {
            "occurred": 1 or 0,
            "within_laps": int or None (laps until overtake)
        }
    """
    # Check next N laps
    for delta in range(1, lookahead + 1):
        future_lap_num = lap_num + delta
        future_lap = df[df["lap_number"] == future_lap_num]

        if future_lap.empty:
            break  # No more laps

        ahead_future = future_lap[future_lap["driver_id"] == driver_ahead_id]
        behind_future = future_lap[future_lap["driver_id"] == driver_behind_id]

        if ahead_future.empty or behind_future.empty:
            continue

        # Check cumulative times (lower = ahead)
        ahead_time = ahead_future.iloc[0]["cumulative_time"]
        behind_time = behind_future.iloc[0]["cumulative_time"]

        # Overtake occurred if previously-behind driver now has lower cumulative time
        if behind_time < ahead_time:
            return {"occurred": 1, "within_laps": delta}

    return {"occurred": 0, "within_laps": None}


def _calculate_tyre_advantage(compound_behind: Optional[str], compound_ahead: Optional[str]) -> Optional[int]:
    """
    Calculate tyre advantage for the attacking (behind) driver.

    Returns:
        Positive = advantage to behind (softer tyre)
        Negative = disadvantage to behind (harder tyre)
        None = missing data
    """
    if not compound_behind or not compound_ahead:
        return None

    value_behind = COMPOUND_VALUES.get(compound_behind)
    value_ahead = COMPOUND_VALUES.get(compound_ahead)

    if value_behind is None or value_ahead is None:
        return None

    # Lower value = softer tyre = advantage
    # So advantage = value_ahead - value_behind
    return int(value_ahead - value_behind)
