"""
F1 Intelligence Hub - Track Status Database Models

Track status data: RaceControl, Incident
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class RaceControl(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Race Control Message.

    Represents official race control messages (flags, safety car, DRS, etc.).
    """

    __tablename__ = "race_control"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)  # When the message was issued
    category = Column(String(50), nullable=False)  # Flag, SafetyCar, DRS, etc.
    message = Column(Text, nullable=False)  # Full message text
    flag = Column(String(20), nullable=True)  # GREEN, YELLOW, RED, BLUE, etc.
    scope = Column(String(20), nullable=True)  # Track, Sector, Driver

    # Relationships
    session = relationship("Session", back_populates="race_control")

    def __repr__(self) -> str:
        return f"<RaceControl(session_id={self.session_id}, category={self.category}, flag={self.flag})>"


class Incident(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Incident.

    Represents on-track incidents (collisions, offs, investigations, penalties).
    """

    __tablename__ = "incidents"

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=True)  # Null for multi-car incidents
    incident_type = Column(String(50), nullable=False)  # Collision, TrackLimits, Investigation, Penalty, etc.
    description = Column(Text, nullable=False)
    lap_number = Column(String(20), nullable=True)  # Lap when incident occurred

    # Relationships
    session = relationship("Session", back_populates="incidents")

    def __repr__(self) -> str:
        return f"<Incident(session_id={self.session_id}, type={self.incident_type}, driver={self.driver_id})>"
