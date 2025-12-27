"""
F1 Intelligence Hub - Database Models

SQLAlchemy ORM models for all database tables.
"""

from .base import TimestampMixin, UUIDPrimaryKeyMixin
from .core import Constructor, Driver, Event, Season, Session
from .features import BattleFeature, LapFeature, StintFeature
from .llm import ChatMessage, ChatSession, Document, Embedding
from .models import ModelRegistry, Prediction
from .timing import Lap, Stint
from .track_status import Incident, RaceControl

__all__ = [
    # Base mixins
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    # Core models
    "Season",
    "Driver",
    "Constructor",
    "Event",
    "Session",
    # Timing models
    "Lap",
    "Stint",
    # Track status models
    "RaceControl",
    "Incident",
    # Feature models
    "LapFeature",
    "StintFeature",
    "BattleFeature",
    # ML models
    "ModelRegistry",
    "Prediction",
    # LLM/RAG models
    "Document",
    "Embedding",
    "ChatSession",
    "ChatMessage",
]
