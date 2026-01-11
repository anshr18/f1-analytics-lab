"""
F1 Intelligence Hub - Core Database Models

Core entities: Season, Driver, Constructor, Event, Session
"""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class Season(Base, TimestampMixin):
    """
    F1 Season.

    Represents a single F1 championship season.
    """

    __tablename__ = "seasons"

    year = Column(Integer, primary_key=True, nullable=False)
    events = relationship("Event", back_populates="season", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Season(year={self.year})>"


class Driver(Base, TimestampMixin):
    """
    F1 Driver.

    Represents a driver with their metadata.
    """

    __tablename__ = "drivers"

    driver_id = Column(String(50), primary_key=True, nullable=False)  # e.g., "max_verstappen"
    full_name = Column(String(100), nullable=False)  # e.g., "Max Verstappen"
    abbreviation = Column(String(3), nullable=False)  # e.g., "VER"
    number = Column(Integer, nullable=True)  # Permanent race number
    country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3 country code

    # Relationships
    laps = relationship("Lap", back_populates="driver")
    stints = relationship("Stint", back_populates="driver")

    def __repr__(self) -> str:
        return f"<Driver(driver_id={self.driver_id}, name={self.full_name})>"


class Constructor(Base, TimestampMixin):
    """
    F1 Constructor (Team).

    Represents a constructor/team.
    """

    __tablename__ = "constructors"

    constructor_id = Column(String(50), primary_key=True, nullable=False)  # e.g., "red_bull"
    name = Column(String(100), nullable=False)  # e.g., "Red Bull Racing"
    country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3 country code

    def __repr__(self) -> str:
        return f"<Constructor(constructor_id={self.constructor_id}, name={self.name})>"


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    F1 Event (Grand Prix Weekend).

    Represents a single race weekend with multiple sessions.
    """

    __tablename__ = "events"

    season_year = Column(Integer, ForeignKey("seasons.year"), nullable=False)
    round_number = Column(Integer, nullable=False)  # Round number in season (1-24)
    event_name = Column(String(100), nullable=False)  # e.g., "Bahrain Grand Prix"
    country = Column(String(100), nullable=False)  # e.g., "Bahrain"
    location = Column(String(100), nullable=False)  # e.g., "Sakhir"
    event_date = Column(Date, nullable=False)  # Date of the race

    # Relationships
    season = relationship("Season", back_populates="events")
    sessions = relationship("Session", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Event(year={self.season_year}, round={self.round_number}, name={self.event_name})>"


class Session(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    F1 Session.

    Represents a single session within an event (FP1, FP2, FP3, Q, Sprint, Race).
    """

    __tablename__ = "sessions"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    session_type = Column(String(20), nullable=False)  # FP1, FP2, FP3, Q, Sprint, Race
    session_date = Column(Date, nullable=False)
    is_ingested = Column(Boolean, default=False, nullable=False)  # Whether data has been loaded
    source = Column(String(50), nullable=True)  # fastf1, openf1, jolpica

    # Relationships
    event = relationship("Event", back_populates="sessions")
    laps = relationship("Lap", back_populates="session", cascade="all, delete-orphan")
    stints = relationship("Stint", back_populates="session", cascade="all, delete-orphan")
    race_control = relationship("RaceControl", back_populates="session", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Session(event_id={self.event_id}, type={self.session_type}, ingested={self.is_ingested})>"
