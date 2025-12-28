"""
Pit Strategy Service

Calculates optimal pit stop strategies, undercut/overcut opportunities,
and compares different compound strategies.
"""

from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session

from f1hub.ml.models.lap_time import LapTimeModel
from f1hub.ml.models.tyre_degradation import TyreDegradationModel


@dataclass
class UndercutResult:
    """Result of undercut/overcut calculation"""

    time_delta: float  # Positive = attacker gains, negative = defender gains
    optimal_pit_lap: int
    success_probability: float
    attacker_outlap: float  # First lap after pit
    defender_response_lap: int
    net_positions: dict[str, int]  # Final predicted positions
    lap_by_lap: list[dict]  # Detailed lap-by-lap breakdown


class PitStrategyService:
    """
    Service for calculating pit stop strategies and undercut/overcut scenarios.

    Uses ML models to predict lap times and tyre degradation to simulate
    different pit stop strategies.
    """

    # Constants from F1 regulations and typical pit stop characteristics
    PIT_LOSS_TIME = 22.0  # Average time lost in pit lane (seconds)
    TYRE_WARM_UP_LAPS = 2  # Laps to reach optimal tyre temperature
    TYRE_WARM_UP_PENALTY = 0.5  # Seconds slower per warm-up lap

    def __init__(self, db: Session):
        """
        Initialize pit strategy service.

        Args:
            db: Database session for querying lap/stint data
        """
        self.db = db
        self.lap_time_model = LapTimeModel()
        self.tyre_deg_model = TyreDegradationModel()

    def calculate_undercut(
        self,
        session_id: str,
        attacking_driver: str,
        defending_driver: str,
        current_lap: int,
        gap_seconds: float,
        tyre_age_attacker: int,
        tyre_age_defender: int,
        attacker_compound: str = "SOFT",
        defender_compound: str = "MEDIUM",
        track_status: str = "GREEN",
    ) -> UndercutResult:
        """
        Calculate undercut opportunity for attacking driver pitting earlier.

        The undercut works by:
        1. Attacker pits first, gets fresh tyres
        2. Attacker pushes hard on fresh tyres while defender continues on old tyres
        3. Defender pits later, emerges behind if attacker gained enough time

        Args:
            session_id: Session ID for context
            attacking_driver: Driver attempting undercut
            defending_driver: Driver defending position
            current_lap: Current race lap
            gap_seconds: Current gap between drivers
            tyre_age_attacker: Attacker's current tyre age
            tyre_age_defender: Defender's current tyre age
            attacker_compound: Tyre compound attacker will use
            defender_compound: Tyre compound defender will use
            track_status: Track status (GREEN, YELLOW, etc.)

        Returns:
            UndercutResult with detailed strategy analysis
        """
        # Calculate optimal pit lap for attacker (typically when gap is manageable)
        optimal_pit_lap = current_lap + 1

        # Simulate lap-by-lap for next 10 laps to find best opportunity
        best_result = None
        best_time_delta = float('-inf')

        for pit_lap in range(current_lap + 1, current_lap + 11):
            result = self._simulate_undercut_scenario(
                session_id=session_id,
                attacking_driver=attacking_driver,
                defending_driver=defending_driver,
                attacker_pit_lap=pit_lap,
                current_lap=current_lap,
                gap_seconds=gap_seconds,
                tyre_age_attacker=tyre_age_attacker,
                tyre_age_defender=tyre_age_defender,
                attacker_compound=attacker_compound,
                defender_compound=defender_compound,
                track_status=track_status,
            )

            if result["time_delta"] > best_time_delta:
                best_time_delta = result["time_delta"]
                best_result = result
                optimal_pit_lap = pit_lap

        # Calculate success probability based on time delta
        # Success if attacker gains more than the gap + safety margin
        safety_margin = 2.0  # Need 2s buffer to ensure clean overtake
        required_gain = gap_seconds + safety_margin
        success_prob = min(1.0, max(0.0, (best_time_delta / required_gain)))

        return UndercutResult(
            time_delta=best_time_delta,
            optimal_pit_lap=optimal_pit_lap,
            success_probability=success_prob,
            attacker_outlap=best_result["attacker_outlap"],
            defender_response_lap=best_result["defender_response_lap"],
            net_positions=best_result["positions"],
            lap_by_lap=best_result["lap_by_lap"],
        )

    def _simulate_undercut_scenario(
        self,
        session_id: str,
        attacking_driver: str,
        defending_driver: str,
        attacker_pit_lap: int,
        current_lap: int,
        gap_seconds: float,
        tyre_age_attacker: int,
        tyre_age_defender: int,
        attacker_compound: str,
        defender_compound: str,
        track_status: str,
    ) -> dict:
        """
        Simulate a specific undercut scenario lap-by-lap.

        Returns:
            Dictionary with simulation results
        """
        # Assume defender pits 3 laps after attacker (typical response time)
        defender_pit_lap = attacker_pit_lap + 3

        lap_by_lap = []
        cumulative_gap = gap_seconds

        attacker_tyre_age = tyre_age_attacker
        defender_tyre_age = tyre_age_defender

        attacker_compound_current = attacker_compound if current_lap >= attacker_pit_lap else "UNKNOWN"
        defender_compound_current = defender_compound if current_lap >= defender_pit_lap else "UNKNOWN"

        # Simulate each lap
        for lap in range(current_lap, attacker_pit_lap + 10):
            # Attacker's lap time
            if lap == attacker_pit_lap:
                # Pit lap - add pit loss time
                attacker_lap_time = self._predict_lap_time(
                    session_id, attacking_driver, attacker_tyre_age,
                    attacker_compound_current, track_status, position=2
                ) + self.PIT_LOSS_TIME
                attacker_tyre_age = 0  # Fresh tyres
            elif lap < attacker_pit_lap:
                # Before pit - old tyres degrading
                attacker_lap_time = self._predict_lap_time(
                    session_id, attacking_driver, attacker_tyre_age,
                    attacker_compound_current, track_status, position=2
                )
                attacker_tyre_age += 1
            else:
                # After pit - fresh tyres with possible warm-up penalty
                laps_since_pit = lap - attacker_pit_lap
                warm_up_penalty = max(0, (self.TYRE_WARM_UP_LAPS - laps_since_pit) * self.TYRE_WARM_UP_PENALTY)
                attacker_lap_time = self._predict_lap_time(
                    session_id, attacking_driver, laps_since_pit,
                    attacker_compound, track_status, position=2
                ) + warm_up_penalty
                attacker_tyre_age = laps_since_pit

            # Defender's lap time
            if lap == defender_pit_lap:
                defender_lap_time = self._predict_lap_time(
                    session_id, defending_driver, defender_tyre_age,
                    defender_compound_current, track_status, position=1
                ) + self.PIT_LOSS_TIME
                defender_tyre_age = 0
            elif lap < defender_pit_lap:
                defender_lap_time = self._predict_lap_time(
                    session_id, defending_driver, defender_tyre_age,
                    defender_compound_current, track_status, position=1
                )
                defender_tyre_age += 1
            else:
                laps_since_pit = lap - defender_pit_lap
                warm_up_penalty = max(0, (self.TYRE_WARM_UP_LAPS - laps_since_pit) * self.TYRE_WARM_UP_PENALTY)
                defender_lap_time = self._predict_lap_time(
                    session_id, defending_driver, laps_since_pit,
                    defender_compound, track_status, position=1
                ) + warm_up_penalty
                defender_tyre_age = laps_since_pit

            # Update gap
            lap_delta = defender_lap_time - attacker_lap_time
            cumulative_gap += lap_delta

            lap_by_lap.append({
                "lap": lap,
                "attacker_lap_time": attacker_lap_time,
                "defender_lap_time": defender_lap_time,
                "lap_delta": lap_delta,
                "cumulative_gap": cumulative_gap,
                "attacker_tyre_age": attacker_tyre_age,
                "defender_tyre_age": defender_tyre_age,
            })

        # Determine final positions based on final gap
        final_gap = cumulative_gap
        positions = {
            attacking_driver: 1 if final_gap < 0 else 2,  # Negative gap means ahead
            defending_driver: 2 if final_gap < 0 else 1,
        }

        # Time delta is how much time attacker gained (positive = good for attacker)
        time_delta = gap_seconds - final_gap

        # Get attacker's outlap time (first lap after pit)
        attacker_outlap = None
        for lap_data in lap_by_lap:
            if lap_data["lap"] == attacker_pit_lap + 1:
                attacker_outlap = lap_data["attacker_lap_time"]
                break

        return {
            "time_delta": time_delta,
            "attacker_outlap": attacker_outlap or 0.0,
            "defender_response_lap": defender_pit_lap,
            "positions": positions,
            "lap_by_lap": lap_by_lap,
        }

    def _predict_lap_time(
        self,
        session_id: str,
        driver_id: str,
        tyre_age: int,
        compound: str,
        track_status: str,
        position: int,
    ) -> float:
        """
        Predict lap time using the trained ML model.

        Args:
            session_id: Session ID for context
            driver_id: Driver abbreviation
            tyre_age: Age of tyres in laps
            compound: Tyre compound
            track_status: Track condition
            position: Current position

        Returns:
            Predicted lap time in seconds
        """
        try:
            # Use the lap time ML model to predict
            prediction = self.lap_time_model.predict({
                "tyre_age": tyre_age,
                "compound": compound,
                "track_status": track_status,
                "position": position,
                "driver_id": driver_id,
            })
            return prediction.predicted_lap_time
        except Exception as e:
            # Fallback to reasonable estimate if model fails
            # Base time + degradation
            base_time = 90.0  # Typical F1 lap time
            compound_delta = {
                "SOFT": -0.5,
                "MEDIUM": 0.0,
                "HARD": 0.5,
            }.get(compound, 0.0)
            deg_penalty = tyre_age * 0.05  # 0.05s per lap degradation
            return base_time + compound_delta + deg_penalty
