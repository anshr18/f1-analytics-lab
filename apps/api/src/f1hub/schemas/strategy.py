"""
Strategy API Schemas

Pydantic models for strategy simulation requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class UndercutRequest(BaseModel):
    """Request for undercut/overcut calculation"""

    session_id: str = Field(..., description="Session ID for context")
    attacking_driver: str = Field(..., description="Driver attempting undercut (e.g., 'VER')")
    defending_driver: str = Field(..., description="Driver defending position (e.g., 'LEC')")
    current_lap: int = Field(..., ge=1, description="Current race lap number")
    gap_seconds: float = Field(..., gt=0, description="Current gap between drivers in seconds")
    tyre_age_attacker: int = Field(..., ge=0, description="Attacker's current tyre age in laps")
    tyre_age_defender: int = Field(..., ge=0, description="Defender's current tyre age in laps")
    attacker_compound: str = Field(default="SOFT", description="Tyre compound for attacker")
    defender_compound: str = Field(default="MEDIUM", description="Tyre compound for defender")
    track_status: str = Field(default="GREEN", description="Track status")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "attacking_driver": "VER",
                "defending_driver": "LEC",
                "current_lap": 25,
                "gap_seconds": 3.2,
                "tyre_age_attacker": 15,
                "tyre_age_defender": 12,
                "attacker_compound": "SOFT",
                "defender_compound": "MEDIUM",
                "track_status": "GREEN",
            }
        }


class LapDetail(BaseModel):
    """Lap-by-lap details in strategy simulation"""

    lap: int
    attacker_lap_time: float
    defender_lap_time: float
    lap_delta: float = Field(..., description="Time difference this lap (positive = attacker faster)")
    cumulative_gap: float = Field(..., description="Total gap between drivers")
    attacker_tyre_age: int
    defender_tyre_age: int


class UndercutResponse(BaseModel):
    """Response from undercut/overcut calculation"""

    time_delta: float = Field(
        ...,
        description="Net time gained by attacker (positive = undercut works, negative = fails)"
    )
    optimal_pit_lap: int = Field(..., description="Optimal lap for attacker to pit")
    success_probability: float = Field(..., ge=0, le=1, description="Probability of successful undercut")
    attacker_outlap: float = Field(..., description="Attacker's first lap time after pit stop")
    defender_response_lap: int = Field(..., description="Expected lap for defender to respond")
    net_positions: dict[str, int] = Field(..., description="Final predicted positions")
    lap_by_lap: list[LapDetail] = Field(..., description="Detailed lap-by-lap breakdown")

    class Config:
        json_schema_extra = {
            "example": {
                "time_delta": 2.5,
                "optimal_pit_lap": 26,
                "success_probability": 0.78,
                "attacker_outlap": 92.3,
                "defender_response_lap": 29,
                "net_positions": {"VER": 1, "LEC": 2},
                "lap_by_lap": [
                    {
                        "lap": 25,
                        "attacker_lap_time": 91.5,
                        "defender_lap_time": 91.2,
                        "lap_delta": -0.3,
                        "cumulative_gap": 3.5,
                        "attacker_tyre_age": 15,
                        "defender_tyre_age": 12,
                    }
                ],
            }
        }


# Safety Car Strategy Schemas


class DriverStateInput(BaseModel):
    """Current state of a driver during safety car period"""

    driver_id: str = Field(..., description="Driver identifier (e.g., 'VER')")
    position: int = Field(..., ge=1, le=20, description="Current race position")
    tyre_age: int = Field(..., ge=0, description="Current tyre age in laps")
    compound: str = Field(..., description="Current tyre compound")
    gap_to_leader: float = Field(..., ge=0, description="Gap to race leader in seconds")
    gap_to_next: float = Field(..., ge=0, description="Gap to car ahead in seconds")


class SafetyCarRequest(BaseModel):
    """Request for safety car strategy analysis"""

    session_id: str = Field(..., description="Session ID for context")
    safety_car_lap: int = Field(..., ge=1, description="Lap when safety car was deployed")
    total_laps: int = Field(..., ge=1, description="Total race laps")
    driver_states: List[DriverStateInput] = Field(
        ..., min_length=2, description="Current state of all drivers"
    )
    track_status: str = Field(default="SC", description="Track status (SC or VSC)")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "safety_car_lap": 35,
                "total_laps": 57,
                "track_status": "SC",
                "driver_states": [
                    {
                        "driver_id": "VER",
                        "position": 1,
                        "tyre_age": 18,
                        "compound": "MEDIUM",
                        "gap_to_leader": 0.0,
                        "gap_to_next": 0.0,
                    },
                    {
                        "driver_id": "LEC",
                        "position": 2,
                        "tyre_age": 15,
                        "compound": "MEDIUM",
                        "gap_to_leader": 2.5,
                        "gap_to_next": 2.5,
                    },
                ],
            }
        }


class SafetyCarDecisionOutput(BaseModel):
    """Decision recommendation for a specific driver"""

    driver_id: str
    current_position: int
    recommendation: str = Field(..., description="PIT, STAY_OUT, or RISKY")
    predicted_position_if_pit: int
    predicted_position_if_stay: int
    position_gain_if_pit: int
    position_loss_if_pit: int
    tyre_advantage: int = Field(..., description="Laps fresher than average if pit")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in recommendation")
    reasoning: str = Field(..., description="Human-readable reasoning")


class SafetyCarResponse(BaseModel):
    """Response from safety car strategy analysis"""

    safety_car_lap: int
    laps_remaining: int
    drivers_who_should_pit: List[str]
    drivers_who_should_stay: List[str]
    decisions: List[SafetyCarDecisionOutput]
    field_summary: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "safety_car_lap": 35,
                "laps_remaining": 22,
                "drivers_who_should_pit": ["VER", "PER"],
                "drivers_who_should_stay": ["LEC", "NOR"],
                "decisions": [
                    {
                        "driver_id": "VER",
                        "current_position": 1,
                        "recommendation": "PIT",
                        "predicted_position_if_pit": 3,
                        "predicted_position_if_stay": 1,
                        "position_gain_if_pit": 0,
                        "position_loss_if_pit": 2,
                        "tyre_advantage": 15,
                        "confidence": 0.85,
                        "reasoning": "Old tires (18 laps) with long race remaining",
                    }
                ],
                "field_summary": {
                    "total_drivers": 20,
                    "avg_tyre_age": 12.5,
                    "drivers_on_old_tyres": 6,
                    "drivers_on_fresh_tyres": 2,
                    "pit_window_advantage": True,
                    "laps_remaining": 22,
                },
            }
        }


# Race Simulation Schemas


class RaceSimulationRequest(BaseModel):
    """Request for complete race simulation"""

    session_id: str = Field(..., description="Session ID for context")
    total_laps: int = Field(..., ge=1, description="Total race laps")
    drivers: List[str] = Field(..., min_length=2, description="List of driver IDs")
    pit_strategies: Dict[str, List[int]] = Field(
        ..., description="Pit stop laps for each driver (driver_id -> [lap1, lap2, ...])"
    )


class RaceSimulationResponse(BaseModel):
    """Response from race simulation"""

    final_classification: Dict[str, int]
    lap_by_lap_positions: List[Dict[str, int]]
    total_pit_stops: Dict[str, int]
    fastest_lap: Dict[str, Any]
    summary: str
