"""
Race Result Prediction Model

Predicts final finishing position based on qualifying position and driver characteristics.
"""

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from f1hub.ml.base import BaseMLModel

logger = logging.getLogger(__name__)


class RaceResultModel(BaseMLModel):
    """Predicts final finishing position.

    Target: final_position (1-20, multi-class classification)
    Features:
        - grid_position: Starting position from qualifying
        - driver_* : One-hot encoded driver columns
        - avg_lap_time: Average lap time from race (for training)

    Model: XGBoost Multi-class Classifier
    Training data: Race sessions with final positions

    Note: This is a simplified version. A production model would include:
    - Practice session data
    - Team/constructor info
    - Circuit characteristics
    - Historical performance
    """

    def __init__(self):
        """Initialize the race result model."""
        # XGBoost for multi-class classification (positions 1-20)
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=7,
            objective="multi:softprob",
            num_class=20,
            random_state=42,
            verbosity=0,
        )
        self.feature_names: List[str] = []
        self.driver_columns: List[str] = []

    def load_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """Load race results for training.

        Args:
            db: Database session

        Returns:
            Tuple of (X, y) - features and targets
        """
        # Get race sessions with final positions
        # We'll use the last lap of each driver as their final position
        query = """
            WITH final_laps AS (
                SELECT
                    l.session_id,
                    l.driver_id,
                    l.position as final_position,
                    AVG(l2.lap_time) as avg_lap_time,
                    ROW_NUMBER() OVER (PARTITION BY l.session_id, l.driver_id ORDER BY l.lap_number DESC) as rn
                FROM laps l
                JOIN laps l2 ON l2.session_id = l.session_id
                    AND l2.driver_id = l.driver_id
                    AND l2.is_pit_in_lap = FALSE
                    AND l2.is_pit_out_lap = FALSE
                    AND l2.deleted = FALSE
                    AND l2.lap_time IS NOT NULL
                JOIN sessions s ON l.session_id = s.id
                WHERE s.session_type = 'Race'
                    AND l.position IS NOT NULL
                    AND l.deleted = FALSE
                GROUP BY l.session_id, l.driver_id, l.lap_number, l.position
            ),
            first_laps AS (
                SELECT
                    session_id,
                    driver_id,
                    position as grid_position
                FROM laps
                WHERE lap_number = 1
                    AND position IS NOT NULL
                    AND deleted = FALSE
            )
            SELECT
                fl.final_position,
                COALESCE(fl2.grid_position, 20) as grid_position,
                fl.avg_lap_time,
                fl.driver_id
            FROM final_laps fl
            LEFT JOIN first_laps fl2 ON fl.session_id = fl2.session_id
                AND fl.driver_id = fl2.driver_id
            WHERE fl.rn = 1
                AND fl.final_position <= 20
                AND fl.avg_lap_time IS NOT NULL
        """

        df = pd.read_sql(query, db.bind)

        if len(df) == 0:
            raise ValueError("No training data found. Ensure race sessions are ingested.")

        logger.info(f"Loaded {len(df)} race results for training")

        # Convert avg_lap_time interval to seconds
        df["avg_lap_time_seconds"] = df["avg_lap_time"].apply(lambda x: x.total_seconds())

        # One-hot encode driver_id
        df = pd.get_dummies(df, columns=["driver_id"], prefix="driver")

        # Get driver columns for future predictions
        self.driver_columns = [col for col in df.columns if col.startswith("driver_")]

        # Feature columns
        self.feature_names = ["grid_position", "avg_lap_time_seconds"] + self.driver_columns

        X = df[self.feature_names]
        # XGBoost expects classes to be 0-indexed, so subtract 1 from positions
        y = df["final_position"] - 1

        logger.info(f"Training features: {self.feature_names[:5]}... ({len(self.feature_names)} total)")
        logger.info(f"Position distribution: {df['final_position'].value_counts().head()}")

        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train model and return metrics.

        Args:
            X: Training features
            y: Training targets (0-indexed positions)

        Returns:
            Dictionary of metrics (accuracy, top3_accuracy, top5_accuracy)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "top3_accuracy": float(
                top_k_accuracy_score(y_test, y_pred_proba, k=3, labels=np.arange(20))
            ),
            "top5_accuracy": float(
                top_k_accuracy_score(y_test, y_pred_proba, k=5, labels=np.arange(20))
            ),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        logger.info(f"Training complete. Metrics: {metrics}")

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict finishing position.

        Args:
            X: Features to predict on

        Returns:
            Array of predicted positions (0-indexed)
        """
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict position probabilities.

        Args:
            X: Features to predict on

        Returns:
            Array of shape (n_samples, 20) with probabilities for each position
        """
        return self.model.predict_proba(X)

    def get_feature_names(self) -> List[str]:
        """Get required feature names.

        Returns:
            List of feature names
        """
        return self.feature_names

    def prepare_features(
        self,
        grid_position: int,
        avg_lap_time: float,
        driver_id: str,
    ) -> pd.DataFrame:
        """Prepare features for a single prediction.

        Args:
            grid_position: Starting position from qualifying
            avg_lap_time: Expected average lap time (seconds)
            driver_id: Driver identifier

        Returns:
            DataFrame with features ready for prediction
        """
        # Create feature dict
        features = {
            "grid_position": grid_position,
            "avg_lap_time_seconds": avg_lap_time,
        }

        # Add driver one-hot encoding
        for driver_col in self.driver_columns:
            if driver_col == f"driver_{driver_id}":
                features[driver_col] = 1
            else:
                features[driver_col] = 0

        return pd.DataFrame([features])
