"""
Base ML Model

Abstract base class for all machine learning models.
"""

from abc import ABC, abstractmethod
from typing import List

import numpy as np
import pandas as pd


class BaseMLModel(ABC):
    """Base class for all ML models.

    All models must implement train, predict, and get_feature_names methods.
    """

    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Train the model on the given data.

        Args:
            X: Training features
            y: Training targets

        Returns:
            Dictionary of training metrics (e.g., rmse, mae, r2, accuracy)
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions on the given data.

        Args:
            X: Features to predict on

        Returns:
            Array of predictions
        """
        pass

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Get the list of required feature names.

        Returns:
            List of feature names expected by the model
        """
        pass
