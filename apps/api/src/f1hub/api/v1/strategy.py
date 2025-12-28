"""
Strategy API Endpoints

Endpoints for race strategy simulation and decision support.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from f1hub.core.dependencies import get_db
from f1hub.schemas.strategy import UndercutRequest, UndercutResponse
from f1hub.services.strategy import PitStrategyService

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
