"""
Stint Feature Computation

Calculates stint-level features including tyre degradation metrics.
"""

import logging
from typing import List
from uuid import UUID

import numpy as np
from scipy.stats import linregress
from sqlalchemy.orm import Session

from f1hub.db.models.features import StintFeature
from f1hub.db.models.timing import Lap, Stint

logger = logging.getLogger(__name__)


def compute_stint_features(session_id: UUID, db: Session) -> int:
    """
    Compute and insert stint-level features for a session.

    Features:
    - avg_lap_time: Mean lap time (seconds, excludes pit laps)
    - fastest_lap_time: Fastest lap in stint (seconds)
    - slowest_lap_time: Slowest lap in stint (seconds)
    - deg_per_lap: Linear degradation rate (s/lap) via scipy.stats.linregress
    - deg_r_squared: R² of degradation fit (quality metric)
    - fuel_corrected_avg: Avg lap time adjusted for fuel load (estimate)

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Number of features inserted
    """
    # Check if features already exist
    existing_count = (
        db.query(StintFeature)
        .join(Stint)
        .filter(Stint.session_id == session_id)
        .count()
    )

    if existing_count > 0:
        logger.info(f"Stint features already exist for session {session_id}, skipping")
        return 0

    # Get all stints for this session
    stints = db.query(Stint).filter(Stint.session_id == session_id).all()

    logger.info(f"Computing features for {len(stints)} stints")

    features_to_insert: List[StintFeature] = []

    for stint in stints:
        # Get all non-pit laps for this stint
        laps = (
            db.query(Lap)
            .filter(
                Lap.stint_id == stint.id,
                Lap.is_pit_in_lap == False,  # noqa: E712
                Lap.is_pit_out_lap == False,  # noqa: E712
                Lap.deleted == False,  # noqa: E712
                Lap.lap_time != None,  # noqa: E711
            )
            .order_by(Lap.lap_number)
            .all()
        )

        if len(laps) < 3:
            # Need at least 3 laps for meaningful features
            logger.debug(f"Skipping stint {stint.id} - only {len(laps)} valid laps")
            continue

        # Extract lap times in seconds
        lap_times_seconds = [lap.lap_time.total_seconds() for lap in laps]
        lap_numbers = [lap.lap_number for lap in laps]

        # Calculate basic statistics
        avg_lap_time = float(np.mean(lap_times_seconds))
        fastest_lap_time = float(np.min(lap_times_seconds))
        slowest_lap_time = float(np.max(lap_times_seconds))

        # Calculate degradation using linear regression
        # lap_time ~ lap_number within stint
        # slope = deg_per_lap (seconds per lap)
        deg_per_lap = None
        deg_r_squared = None

        if len(laps) >= 5:
            # Only calculate degradation for stints with enough laps
            try:
                # Use lap indices within stint (0, 1, 2, ...) for regression
                lap_indices = list(range(len(laps)))

                slope, intercept, r_value, p_value, std_err = linregress(
                    lap_indices, lap_times_seconds
                )

                deg_per_lap = float(slope)  # seconds/lap
                deg_r_squared = float(r_value**2)  # R² goodness of fit

                logger.debug(
                    f"Stint {stint.id}: deg={deg_per_lap:.4f} s/lap, R²={deg_r_squared:.3f}"
                )

            except Exception as e:
                logger.warning(f"Failed to calculate degradation for stint {stint.id}: {e}")

        # Fuel correction (approximation)
        # Assume ~0.03s/lap fuel effect (F1 loses ~0.03s per lap as fuel burns)
        # This is a rough estimate - actual effect varies by circuit
        fuel_corrected_avg = None
        if deg_per_lap is not None and len(laps) > 0:
            # Average lap index in stint
            avg_lap_index = len(laps) / 2
            # Estimate fuel correction: assume 0.03s benefit per lap
            fuel_correction = avg_lap_index * 0.03
            fuel_corrected_avg = float(avg_lap_time - fuel_correction)

        # Create feature record
        feature = StintFeature(
            stint_id=stint.id,
            avg_lap_time=avg_lap_time,
            fastest_lap_time=fastest_lap_time,
            slowest_lap_time=slowest_lap_time,
            deg_per_lap=deg_per_lap,
            deg_r_squared=deg_r_squared,
            fuel_corrected_avg=fuel_corrected_avg,
            extra_features={
                "lap_count": len(laps),
                "compound": stint.compound,
                "driver_id": stint.driver_id,
            },
        )

        features_to_insert.append(feature)

    # Bulk insert
    if features_to_insert:
        db.bulk_save_objects(features_to_insert)
        db.flush()

    logger.info(f"Inserted {len(features_to_insert)} stint features")

    return len(features_to_insert)
