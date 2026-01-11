"""
Race Simulation Engine

Simulates complete race scenarios with multiple pit stops and strategic decisions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session


@dataclass
class RaceSimulationRequest:
    """Input parameters for race simulation"""

    session_id: str
    total_laps: int
    drivers: List[str]
    pit_strategies: Dict[str, List[int]]  # driver_id -> [pit_lap_1, pit_lap_2, ...]


@dataclass
class RaceSimulationResult:
    """Complete race simulation results"""

    final_classification: Dict[str, int]  # driver_id -> final_position
    lap_by_lap_positions: List[Dict[str, int]]  # List of position snapshots per lap
    total_pit_stops: Dict[str, int]  # driver_id -> number of stops
    fastest_lap: Dict[str, any]  # driver, lap_number, time
    summary: str


class RaceSimulationEngine:
    """
    Engine for simulating complete F1 races.

    Simplified simulation that tracks positions through pit stops.
    """

    PIT_LOSS_TIME = 22.0  # Average pit stop time loss (seconds)

    def __init__(self, db: Session):
        self.db = db

    def simulate_race(
        self,
        session_id: str,
        total_laps: int,
        drivers: List[str],
        pit_strategies: Dict[str, List[int]],
    ) -> RaceSimulationResult:
        """
        Simulate a complete race with given pit strategies.

        Args:
            session_id: Session context
            total_laps: Total race laps
            drivers: List of driver IDs
            pit_strategies: Pit stop laps for each driver

        Returns:
            Complete race simulation results
        """
        # Initialize positions (grid order)
        current_positions = {driver: idx + 1 for idx, driver in enumerate(drivers)}
        lap_by_lap = []

        # Simulate each lap
        for lap in range(1, total_laps + 1):
            # Track who pits this lap
            pitting_drivers = [
                driver for driver, stops in pit_strategies.items()
                if lap in stops
            ]

            # Apply pit stop penalty (drivers who pit drop positions)
            for driver in pitting_drivers:
                # Count how many drivers ahead are NOT pitting
                drivers_ahead_staying = sum(
                    1 for d in drivers
                    if current_positions[d] < current_positions[driver]
                    and d not in pitting_drivers
                )

                # Simplified: pit stop costs ~3-4 positions
                penalty_positions = min(3, drivers_ahead_staying)
                current_positions[driver] += penalty_positions

            # Re-sort positions
            sorted_drivers = sorted(drivers, key=lambda d: current_positions[d])
            current_positions = {driver: idx + 1 for idx, driver in enumerate(sorted_drivers)}

            # Record lap positions
            lap_by_lap.append(current_positions.copy())

        # Calculate final results
        total_stops = {driver: len(stops) for driver, stops in pit_strategies.items()}

        # Find fastest lap (placeholder)
        fastest_lap = {
            "driver": drivers[0],
            "lap_number": total_laps // 2,
            "time": 90.5,
        }

        # Generate summary
        winner = sorted_drivers[0]
        summary = f"{winner} wins! Simulated {total_laps} laps with {len(drivers)} drivers."

        return RaceSimulationResult(
            final_classification=current_positions,
            lap_by_lap_positions=lap_by_lap,
            total_pit_stops=total_stops,
            fastest_lap=fastest_lap,
            summary=summary,
        )
