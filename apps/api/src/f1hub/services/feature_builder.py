"""
Feature Builder Service

Orchestrates feature computation for ML models.
"""

import logging
import time
from uuid import UUID

from sqlalchemy.orm import Session

from f1hub.ml.features import (
    compute_battle_features,
    compute_lap_features,
    compute_stint_features,
)

logger = logging.getLogger(__name__)


class FeatureBuilderService:
    """Orchestrates feature computation for ML models."""

    def __init__(self, db: Session):
        """
        Initialize feature builder service.

        Args:
            db: Database session
        """
        self.db = db

    def build_features_for_session(self, session_id: UUID) -> dict:
        """
        Compute all features for a session.

        This will:
        1. Compute lap-level features (time deltas, tyre age, etc.)
        2. Compute stint-level features (degradation, avg lap time, etc.)
        3. Compute battle features (overtake detection, gaps, etc.)

        Args:
            session_id: Session UUID

        Returns:
            {
                "session_id": "...",
                "lap_features_count": 1129,
                "stint_features_count": 46,
                "battle_features_count": 234,
                "duration_seconds": 12.4,
                "errors": []
            }
        """
        start_time = time.time()
        errors = []

        logger.info(f"Building features for session {session_id}")

        # Compute lap features
        try:
            lap_count = compute_lap_features(session_id, self.db)
            logger.info(f"Computed {lap_count} lap features")
        except Exception as e:
            error_msg = f"Failed to compute lap features: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            lap_count = 0

        # Compute stint features
        try:
            stint_count = compute_stint_features(session_id, self.db)
            logger.info(f"Computed {stint_count} stint features")
        except Exception as e:
            error_msg = f"Failed to compute stint features: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            stint_count = 0

        # Compute battle features
        try:
            battle_count = compute_battle_features(session_id, self.db)
            logger.info(f"Computed {battle_count} battle features")
        except Exception as e:
            error_msg = f"Failed to compute battle features: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            battle_count = 0

        # Commit all changes
        try:
            self.db.commit()
            logger.info("Feature computation committed successfully")
        except Exception as e:
            error_msg = f"Failed to commit features: {e}"
            logger.error(error_msg, exc_info=True)
            self.db.rollback()
            errors.append(error_msg)

        duration = time.time() - start_time

        result = {
            "session_id": str(session_id),
            "lap_features_count": lap_count,
            "stint_features_count": stint_count,
            "battle_features_count": battle_count,
            "duration_seconds": round(duration, 2),
            "errors": errors,
        }

        logger.info(f"Feature computation complete: {result}")

        return result
