"""
Lap Time Prediction Model

Predicts lap time given current conditions (tyre age, compound, track status, etc.).
"""

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from f1hub.ml.base import BaseMLModel

logger = logging.getLogger(__name__)


class LapTimeModel(BaseMLModel):
    """Predicts lap time given current state.

    Target: lap_time (seconds)
    Features:
        - tyre_age: Laps completed on current tyre
        - compound_code: Encoded compound (SOFT=1, MEDIUM=2, HARD=3)
        - track_status_code: Encoded track status (Green=1, Yellow=2, SC=3, VSC=4, Red=5)
        - position: Current race position
        - driver_* : One-hot encoded driver columns

    Model: XGBoost Regressor
    Training data: Laps with valid lap times (not pit laps, not deleted)
    """

    def __init__(self):
        """Initialize the lap time model."""
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            random_state=42,
            verbosity=0,  # Suppress XGBoost warnings
        )
        self.feature_names: List[str] = []
        self.driver_columns: List[str] = []

    def load_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """Load lap features for training.

        Args:
            db: Database session

        Returns:
            Tuple of (X, y) - features and targets
        """
        query = """
            SELECT
                l.lap_time,
                lf.tyre_age,
                lf.compound_code,
                lf.track_status_code,
                lf.position,
                l.driver_id
            FROM lap_features lf
            JOIN laps l ON lf.lap_id = l.id
            WHERE l.lap_time IS NOT NULL
                AND l.is_pit_in_lap = FALSE
                AND l.is_pit_out_lap = FALSE
                AND l.deleted = FALSE
                AND lf.tyre_age IS NOT NULL
                AND lf.compound_code IS NOT NULL
                AND lf.track_status_code = 1
        """

        df = pd.read_sql(query, db.bind)

        if len(df) == 0:
            raise ValueError("No training data found. Ensure lap features are computed first.")

        logger.info(f"Loaded {len(df)} laps for training")

        # Convert lap_time interval to seconds
        df["lap_time_seconds"] = df["lap_time"].apply(lambda x: x.total_seconds())

        # One-hot encode driver_id
        df = pd.get_dummies(df, columns=["driver_id"], prefix="driver")

        # Get driver columns for future predictions
        self.driver_columns = [col for col in df.columns if col.startswith("driver_")]

        # Feature columns
        self.feature_names = [
            "tyre_age",
            "compound_code",
            "track_status_code",
            "position",
        ] + self.driver_columns

        X = df[self.feature_names]
        y = df["lap_time_seconds"]

        logger.info(
            f"Training features: {self.feature_names[:5]}... ({len(self.feature_names)} total)"
        )

        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train model and return metrics.

        Args:
            X: Training features
            y: Training targets (lap times in seconds)

        Returns:
            Dictionary of metrics (rmse, mae, r2, train_samples, test_samples)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)

        metrics = {
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        logger.info(f"Training complete. Metrics: {metrics}")

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict lap time.

        Args:
            X: Features to predict on

        Returns:
            Array of predicted lap times in seconds
        """
        return self.model.predict(X)

    def get_feature_names(self) -> List[str]:
        """Get required feature names.

        Returns:
            List of feature names
        """
        return self.feature_names

    def prepare_features(
        self,
        tyre_age: int,
        compound: str,
        track_status: str,
        position: int,
        driver_id: str,
    ) -> pd.DataFrame:
        """Prepare features for a single prediction.

        Args:
            tyre_age: Laps on current tyre
            compound: Tyre compound (SOFT, MEDIUM, HARD)
            track_status: Track status (GREEN, YELLOW, SC, VSC, RED)
            position: Current position
            driver_id: Driver identifier

        Returns:
            DataFrame with features ready for prediction
        """
        compound_map = {"SOFT": 1, "MEDIUM": 2, "HARD": 3}
        track_status_map = {"GREEN": 1, "YELLOW": 2, "SC": 3, "VSC": 4, "RED": 5}

        compound_code = compound_map.get(compound, 2)  # Default to MEDIUM
        track_status_code = track_status_map.get(track_status, 1)  # Default to GREEN

        # Create feature dict
        features = {
            "tyre_age": tyre_age,
            "compound_code": compound_code,
            "track_status_code": track_status_code,
            "position": position,
        }

        # Add driver one-hot encoding
        for driver_col in self.driver_columns:
            if driver_col == f"driver_{driver_id}":
                features[driver_col] = 1
            else:
                features[driver_col] = 0

        return pd.DataFrame([features])
