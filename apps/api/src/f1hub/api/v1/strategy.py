"""
Strategy API Endpoints

Endpoints for race strategy simulation and decision support.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from f1hub.core.dependencies import get_db
from f1hub.schemas.strategy import (
    UndercutRequest,
    UndercutResponse,
    SafetyCarRequest,
    SafetyCarResponse,
    DriverStateInput,
    RaceSimulationRequest,
    RaceSimulationResponse,
)
from f1hub.services.strategy import PitStrategyService, SafetyCarStrategyService, RaceSimulationEngine
from f1hub.services.strategy.safety_car import DriverState

router = APIRouter(prefix="/strategy")


@router.post("/undercut", response_model=UndercutResponse)
async def calculate_undercut(
    request: UndercutRequest,
    db: Session = Depends(get_db),
) -> UndercutResponse:
    """
    Calculate optimal undercut/overcut strategy.

    Simulates lap-by-lap pit stop scenarios to determine if an undercut
    is viable and what the optimal timing would be.

    Args:
        request: Undercut calculation parameters
        db: Database session

    Returns:
        Undercut analysis with optimal pit lap, success probability,
        and detailed lap-by-lap breakdown

    Raises:
        HTTPException: If calculation fails
    """
    try:
        strategy_service = PitStrategyService(db)
        result = strategy_service.calculate_undercut(
            session_id=request.session_id,
            attacking_driver=request.attacking_driver,
            defending_driver=request.defending_driver,
            current_lap=request.current_lap,
            gap_seconds=request.gap_seconds,
            tyre_age_attacker=request.tyre_age_attacker,
            tyre_age_defender=request.tyre_age_defender,
            attacker_compound=request.attacker_compound,
            defender_compound=request.defender_compound,
            track_status=request.track_status,
        )

        return UndercutResponse(
            time_delta=result.time_delta,
            optimal_pit_lap=result.optimal_pit_lap,
            success_probability=result.success_probability,
            attacker_outlap=result.attacker_outlap,
            defender_response_lap=result.defender_response_lap,
            net_positions=result.net_positions,
            lap_by_lap=result.lap_by_lap,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate undercut strategy: {str(e)}"
        )


@router.post("/safety-car", response_model=SafetyCarResponse)
async def analyze_safety_car(
    request: SafetyCarRequest,
    db: Session = Depends(get_db),
) -> SafetyCarResponse:
    """
    Analyze safety car scenario and recommend pit strategies.

    Helps teams make split-second decisions during safety car periods:
    - Should each driver pit or stay out?
    - What positions will they gain/lose?
    - What tire advantage will they have?
    - What is the confidence in each recommendation?

    Args:
        request: Safety car scenario parameters
        db: Database session

    Returns:
        Safety car analysis with recommendations for all drivers

    Raises:
        HTTPException: If analysis fails
    """
    try:
        strategy_service = SafetyCarStrategyService(db)

        # Convert Pydantic models to dataclass
        driver_states = [
            DriverState(
                driver_id=d.driver_id,
                position=d.position,
                tyre_age=d.tyre_age,
                compound=d.compound,
                gap_to_leader=d.gap_to_leader,
                gap_to_next=d.gap_to_next,
            )
            for d in request.driver_states
        ]

        result = strategy_service.analyze_safety_car_scenario(
            session_id=request.session_id,
            safety_car_lap=request.safety_car_lap,
            total_laps=request.total_laps,
            driver_states=driver_states,
            track_status=request.track_status,
        )

        return SafetyCarResponse(
            safety_car_lap=result.safety_car_lap,
            laps_remaining=result.laps_remaining,
            drivers_who_should_pit=result.drivers_who_should_pit,
            drivers_who_should_stay=result.drivers_who_should_stay,
            decisions=[
                {
                    "driver_id": d.driver_id,
                    "current_position": d.current_position,
                    "recommendation": d.recommendation,
                    "predicted_position_if_pit": d.predicted_position_if_pit,
                    "predicted_position_if_stay": d.predicted_position_if_stay,
                    "position_gain_if_pit": d.position_gain_if_pit,
                    "position_loss_if_pit": d.position_loss_if_pit,
                    "tyre_advantage": d.tyre_advantage,
                    "confidence": d.confidence,
                    "reasoning": d.reasoning,
                }
                for d in result.decisions
            ],
            field_summary=result.field_summary,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze safety car scenario: {str(e)}"
        )


@router.post("/race-simulation", response_model=RaceSimulationResponse)
async def simulate_race(
    request: RaceSimulationRequest,
    db: Session = Depends(get_db),
) -> RaceSimulationResponse:
    """
    Simulate complete race with pit strategies.

    Models an entire race from start to finish with given pit stop strategies.
    Tracks position changes lap-by-lap.

    Args:
        request: Race simulation parameters
        db: Database session

    Returns:
        Complete race simulation with final classification

    Raises:
        HTTPException: If simulation fails
    """
    try:
        engine = RaceSimulationEngine(db)
        result = engine.simulate_race(
            session_id=request.session_id,
            total_laps=request.total_laps,
            drivers=request.drivers,
            pit_strategies=request.pit_strategies,
        )

        return RaceSimulationResponse(
            final_classification=result.final_classification,
            lap_by_lap_positions=result.lap_by_lap_positions,
            total_pit_stops=result.total_pit_stops,
            fastest_lap=result.fastest_lap,
            summary=result.summary,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to simulate race: {str(e)}"
        )
