"""
F1 Intelligence Hub - Feature Store Database Models

Feature engineering tables: LapFeature, StintFeature, BattleFeature
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class LapFeature(Base, TimestampMixin):
    """
    Lap Features.

    Engineered features for a single lap (used for ML models).
    """

    __tablename__ = "lap_features"

    lap_id = Column(UUID(as_uuid=True), ForeignKey("laps.id"), primary_key=True, nullable=False)

    # Time deltas
    delta_to_leader = Column(Float, nullable=True)  # Seconds behind leader
    delta_to_ahead = Column(Float, nullable=True)  # Seconds behind car ahead
    delta_to_personal_best = Column(Float, nullable=True)  # Seconds off personal best

    # Tyre metrics
    tyre_age = Column(Integer, nullable=True)  # Age of tyres in laps
    compound_code = Column(Integer, nullable=True)  # Encoded compound (1=SOFT, 2=MEDIUM, 3=HARD)

    # Position metrics
    position = Column(Integer, nullable=True)
    positions_gained = Column(Integer, nullable=True)  # Positions gained/lost this lap

    # Track status encoded
    track_status_code = Column(Integer, nullable=True)  # 1=Green, 2=Yellow, 3=SC, 4=VSC, 5=Red

    # Additional features stored as JSON
    extra_features = Column(JSONB, nullable=True)

    # Relationships
    lap = relationship("Lap", back_populates="features")

    def __repr__(self) -> str:
        return f"<LapFeature(lap_id={self.lap_id})>"


class StintFeature(Base, TimestampMixin):
    """
    Stint Features.

    Aggregated features for an entire stint (used for strategy modeling).
    """

    __tablename__ = "stint_features"

    stint_id = Column(UUID(as_uuid=True), ForeignKey("stints.id"), primary_key=True, nullable=False)

    # Performance metrics
    avg_lap_time = Column(Float, nullable=True)  # Average lap time in seconds
    fastest_lap_time = Column(Float, nullable=True)  # Fastest lap in stint (seconds)
    slowest_lap_time = Column(Float, nullable=True)  # Slowest lap in stint (seconds)

    # Degradation metrics
    deg_per_lap = Column(Float, nullable=True)  # Degradation in seconds per lap (linear fit)
    deg_r_squared = Column(Float, nullable=True)  # R² of degradation fit

    # Fuel-corrected performance (if available)
    fuel_corrected_avg = Column(Float, nullable=True)

    # Additional features stored as JSON
    extra_features = Column(JSONB, nullable=True)

    # Relationships
    stint = relationship("Stint", back_populates="features")

    def __repr__(self) -> str:
        return f"<StintFeature(stint_id={self.stint_id}, avg_lap={self.avg_lap_time})>"


class BattleFeature(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Battle Features.

    Features describing driver battles and overtakes (used for battle prediction).
    """

    __tablename__ = "battle_features"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    lap_number = Column(Integer, nullable=False)

    # Drivers involved
    driver_ahead_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)
    driver_behind_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=False)

    # Battle metrics
    gap_seconds = Column(Float, nullable=False)  # Gap between drivers
    closing_rate = Column(Float, nullable=True)  # Rate of gap closure (seconds/lap)

    # Outcome
    overtake_occurred = Column(Integer, nullable=False)  # 0 or 1 (target for ML)
    overtake_within_laps = Column(Integer, nullable=True)  # Laps until overtake (if occurred)

    # Context
    drs_available = Column(Integer, nullable=True)  # 0 or 1
    tyre_advantage = Column(Float, nullable=True)  # Tyre age difference (ahead - behind)

    # Additional features stored as JSON
    extra_features = Column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<BattleFeature(session_id={self.session_id}, lap={self.lap_number}, gap={self.gap_seconds}s)>"
