"""
Tyre Degradation Model

Predicts tyre degradation rate (deg_per_lap) given compound and driver.
"""

import logging
from typing import List, Tuple

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from f1hub.ml.base import BaseMLModel

logger = logging.getLogger(__name__)


class TyreDegradationModel(BaseMLModel):
    """Predicts deg_per_lap given compound and driver.

    Target: deg_per_lap (seconds/lap)
    Features:
        - compound_code: Encoded compound (SOFT=1, MEDIUM=2, HARD=3)
        - driver_* : One-hot encoded driver columns

    Model: LightGBM Regressor
    Training data: Stints with R² > 0.5, total_laps >= 5
    """

    def __init__(self):
        """Initialize the tyre degradation model."""
        self.model = lgb.LGBMRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42,
            verbose=-1,  # Suppress LightGBM warnings
        )
        self.feature_names: List[str] = []
        self.driver_columns: List[str] = []

    def load_training_data(self, db: Session) -> Tuple[pd.DataFrame, pd.Series]:
        """Load stint features with good degradation fits.

        Args:
            db: Database session

        Returns:
            Tuple of (X, y) - features and targets
        """
        query = """
            SELECT
                sf.deg_per_lap,
                sf.deg_r_squared,
                s.compound,
                s.driver_id,
                s.total_laps
            FROM stint_features sf
            JOIN stints s ON sf.stint_id = s.id
            WHERE sf.deg_r_squared > 0.5 AND s.total_laps >= 5
        """

        df = pd.read_sql(query, db.bind)

        if len(df) == 0:
            raise ValueError("No training data found. Ensure features are computed first.")

        logger.info(f"Loaded {len(df)} stints for training")

        # Encode compound: SOFT=1, MEDIUM=2, HARD=3
        compound_map = {"SOFT": 1, "MEDIUM": 2, "HARD": 3}
        df["compound_code"] = df["compound"].map(compound_map)

        # Handle missing compounds (e.g., INTERMEDIATE, WET)
        df = df.dropna(subset=["compound_code"])

        # One-hot encode driver_id
        df = pd.get_dummies(df, columns=["driver_id"], prefix="driver")

        # Get driver columns for future predictions
        self.driver_columns = [col for col in df.columns if col.startswith("driver_")]

        # Feature columns
        self.feature_names = ["compound_code"] + self.driver_columns

        X = df[self.feature_names]
        y = df["deg_per_lap"]

        logger.info(f"Training features: {self.feature_names[:5]}... ({len(self.feature_names)} total)")

        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train model and return metrics.

        Args:
            X: Training features
            y: Training targets

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
        """Predict degradation rate.

        Args:
            X: Features to predict on

        Returns:
            Array of predicted degradation rates
        """
        return self.model.predict(X)

    def get_feature_names(self) -> List[str]:
        """Get required feature names.

        Returns:
            List of feature names
        """
        return self.feature_names

    def prepare_features(self, compound: str, driver_id: str) -> pd.DataFrame:
        """Prepare features for a single prediction.

        Args:
            compound: Tyre compound (SOFT, MEDIUM, HARD)
            driver_id: Driver identifier

        Returns:
            DataFrame with features ready for prediction
        """
        compound_map = {"SOFT": 1, "MEDIUM": 2, "HARD": 3}
        compound_code = compound_map.get(compound, 2)  # Default to MEDIUM

        # Create feature dict
        features = {"compound_code": compound_code}

        # Add driver one-hot encoding
        for driver_col in self.driver_columns:
            if driver_col == f"driver_{driver_id}":
                features[driver_col] = 1
            else:
                features[driver_col] = 0

        return pd.DataFrame([features])
