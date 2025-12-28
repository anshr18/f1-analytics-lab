"""
Strategy API Schemas

Pydantic models for strategy simulation requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional


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
