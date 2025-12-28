"""
Overtake Probability Model

Predicts probability of overtake occurring in next 3 laps.
"""

import logging
from typing import List, Tuple

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from f1hub.ml.base import BaseMLModel

logger = logging.getLogger(__name__)


class OvertakeModel(BaseMLModel):
    """Predicts overtake probability in next 3 laps.

    Target: overtake_occurred (binary: 0/1)
    Features:
        - gap_seconds: Time gap between cars
        - closing_rate: Gap change per lap (s/lap, negative = closing)
        - tyre_advantage: Compound difference (-2 to +2)
        - drs_available: DRS availability (0/1)
        - lap_number: Normalized lap number (0-1)

    Model: LightGBM Classifier with class_weight='balanced'
    Metrics: F1-score, ROC-AUC (handles imbalanced classes)
    Training data: Battle features with labeled overtakes
    """

    def __init__(self):
        """Initialize the overtake model."""
        self.model = lgb.LGBMClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=5,
            class_weight="balanced",  # Handle imbalanced data
            random_state=42,
            verbose=-1,  # Suppress LightGBM warnings
        )
        self.feature_names: List[str] = [
            "gap_seconds",
            "closing_rate",
            "tyre_advantage",
            "drs_available",
            "lap_number_normalized",
        ]

    def load_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """Load battle features for training.

        Args:
            db: Database session

        Returns:
            Tuple of (X, y) - features and targets
        """
        query = """
            SELECT
                gap_seconds,
                closing_rate,
                tyre_advantage,
                drs_available,
                lap_number,
                overtake_occurred
            FROM battle_features
            WHERE gap_seconds IS NOT NULL
                AND closing_rate IS NOT NULL
        """

        df = pd.read_sql(query, db.bind)

        if len(df) == 0:
            raise ValueError("No training data found. Ensure battle features are computed first.")

        logger.info(f"Loaded {len(df)} battle instances for training")
        logger.info(
            f"Overtakes: {df['overtake_occurred'].sum()} ({df['overtake_occurred'].mean()*100:.1f}%)"
        )

        # Normalize lap_number (assume max 60 laps for normalization)
        df["lap_number_normalized"] = df["lap_number"] / 60.0

        X = df[self.feature_names]
        y = df["overtake_occurred"]

        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train model and return metrics.

        Args:
            X: Training features
            y: Training targets (0/1 for overtake)

        Returns:
            Dictionary of metrics (f1_score, roc_auc, precision, recall)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
        logger.info(
            f"Train overtakes: {y_train.sum()} ({y_train.mean()*100:.1f}%), "
            f"Test overtakes: {y_test.sum()} ({y_test.mean()*100:.1f}%)"
        )

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        metrics = {
            "f1_score": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_overtakes": int(y_train.sum()),
            "test_overtakes": int(y_test.sum()),
        }

        # Log classification report
        logger.info("\nClassification Report:")
        logger.info("\n" + classification_report(y_test, y_pred))

        logger.info(f"Training complete. Metrics: {metrics}")

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict overtake probability.

        Args:
            X: Features to predict on

        Returns:
            Array of probabilities (0-1)
        """
        return self.model.predict_proba(X)[:, 1]

    def get_feature_names(self) -> List[str]:
        """Get required feature names.

        Returns:
            List of feature names
        """
        return self.feature_names

    def prepare_features(
        self,
        gap_seconds: float,
        closing_rate: float,
        tyre_advantage: int,
        drs_available: bool,
        lap_number: int,
    ) -> pd.DataFrame:
        """Prepare features for a single prediction.

        Args:
            gap_seconds: Time gap between cars (seconds)
            closing_rate: Gap change per lap (s/lap)
            tyre_advantage: Compound advantage (-2 to +2)
            drs_available: Whether DRS is available
            lap_number: Current lap number

        Returns:
            DataFrame with features ready for prediction
        """
        features = {
            "gap_seconds": gap_seconds,
            "closing_rate": closing_rate,
            "tyre_advantage": tyre_advantage,
            "drs_available": 1 if drs_available else 0,
            "lap_number_normalized": lap_number / 60.0,
        }

        return pd.DataFrame([features])
