"""
F1 Intelligence Hub - Timing Database Models

Timing data: Lap, Stint
"""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Interval, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class Lap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    F1 Lap.

    Represents a single lap of telemetry data.
    """

    __tablename__ = "laps"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    lap_number = Column(Integer, nullable=False)

    # Timing
    lap_time = Column(Interval, nullable=True)  # Total lap time
    sector_1_time = Column(Interval, nullable=True)
    sector_2_time = Column(Interval, nullable=True)
    sector_3_time = Column(Interval, nullable=True)

    # Tyre information
    compound = Column(String(20), nullable=True)  # SOFT, MEDIUM, HARD, INTERMEDIATE, WET
    tyre_life = Column(Integer, nullable=True)  # Laps on this set of tyres

    # Stint reference
    stint_id = Column(UUID(as_uuid=True), ForeignKey("stints.id"), nullable=True)

    # Track status
    track_status = Column(String(20), nullable=True)  # Green, Yellow, SC, VSC, Red
    is_personal_best = Column(Boolean, default=False)

    # Position
    position = Column(Integer, nullable=True)  # Position at end of lap

    # Flags
    deleted = Column(Boolean, default=False)  # Whether lap was deleted (track limits, etc.)
    is_pit_out_lap = Column(Boolean, default=False)
    is_pit_in_lap = Column(Boolean, default=False)

    # Additional telemetry (stored as JSON)
    telemetry = Column(JSONB, nullable=True)  # Speed, throttle, brake, DRS data

    # Relationships
    session = relationship("Session", back_populates="laps")
    driver = relationship("Driver", back_populates="laps")
    stint = relationship("Stint", back_populates="laps")
    features = relationship("LapFeature", back_populates="lap", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lap(session_id={self.session_id}, driver={self.driver_id}, lap={self.lap_number}, time={self.lap_time})>"


class Stint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    F1 Stint.

    Represents a continuous run on a single set of tyres.
    """

    __tablename__ = "stints"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    stint_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.

    # Tyre information
    compound = Column(String(20), nullable=False)  # SOFT, MEDIUM, HARD, INTERMEDIATE, WET

    # Lap range
    lap_start = Column(Integer, nullable=False)  # First lap of stint
    lap_end = Column(Integer, nullable=True)  # Last lap of stint (null if ongoing)
    total_laps = Column(Integer, nullable=True)  # Total laps in stint

    # Relationships
    session = relationship("Session", back_populates="stints")
    driver = relationship("Driver", back_populates="stints")
    laps = relationship("Lap", back_populates="stint")
    features = relationship("StintFeature", back_populates="stint", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Stint(session_id={self.session_id}, driver={self.driver_id}, stint={self.stint_number}, compound={self.compound})>"
