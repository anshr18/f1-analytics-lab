"""
Live Streaming Models

Database models for real-time race data tracking and WebSocket connections.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import Base


class LiveSession(Base):
    """Live session tracking table."""

    __tablename__ = "live_sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    current_lap = Column(Integer, nullable=True)
    session_status = Column(String(50), nullable=True)  # 'Started', 'Aborted', 'Finished'
    track_status = Column(String(50), nullable=True)  # 'AllClear', 'Yellow', 'Red', 'SCDeployed'
    metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="live_session")
    timing_data = relationship("LiveTiming", back_populates="live_session", cascade="all, delete-orphan")
    events = relationship("LiveEvent", back_populates="live_session", cascade="all, delete-orphan")
    connections = relationship("WebSocketConnection", back_populates="live_session", cascade="all, delete-orphan")


class LiveTiming(Base):
    """Live timing data (position updates)."""

    __tablename__ = "live_timing"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    live_session_id = Column(
        PGUUID(as_uuid=True), ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False
    )
    driver_id = Column(String(3), ForeignKey("drivers.abbreviation", ondelete="CASCADE"), nullable=False)
    lap_number = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    gap_to_leader = Column(Float, nullable=True)  # seconds
    gap_to_ahead = Column(Float, nullable=True)  # seconds
    interval = Column(Float, nullable=True)  # seconds to car ahead
    last_lap_time = Column(Float, nullable=True)  # seconds
    sector1_time = Column(Float, nullable=True)
    sector2_time = Column(Float, nullable=True)
    sector3_time = Column(Float, nullable=True)
    tyre_compound = Column(String(20), nullable=True)
    tyre_age = Column(Integer, nullable=True)
    in_pit = Column(Boolean, nullable=False, default=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(JSONB, nullable=False, default=dict)

    # Relationships
    live_session = relationship("LiveSession", back_populates="timing_data")
    driver = relationship("Driver")


class LiveEvent(Base):
    """Live events (pit stops, incidents, etc.)."""

    __tablename__ = "live_events"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    live_session_id = Column(
        PGUUID(as_uuid=True), ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False
    )
    event_type = Column(String(50), nullable=False)  # 'pit_stop', 'fastest_lap', 'overtake', 'incident'
    lap_number = Column(Integer, nullable=False)
    driver_id = Column(String(3), ForeignKey("drivers.abbreviation", ondelete="CASCADE"), nullable=True)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # 'info', 'warning', 'critical'
    data = Column(JSONB, nullable=False, default=dict)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    live_session = relationship("LiveSession", back_populates="events")
    driver = relationship("Driver")


class WebSocketConnection(Base):
    """WebSocket connections tracking."""

    __tablename__ = "websocket_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    connection_id = Column(String(100), nullable=False, unique=True)
    live_session_id = Column(
        PGUUID(as_uuid=True), ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String(100), nullable=True)
    connected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    disconnected_at = Column(DateTime, nullable=True)
    metadata = Column(JSONB, nullable=False, default=dict)

    # Relationships
    live_session = relationship("LiveSession", back_populates="connections")
