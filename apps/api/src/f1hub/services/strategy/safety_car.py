"""
Safety Car Strategy Service

Analyzes safety car scenarios and recommends optimal pit stop decisions.
Helps teams decide whether to pit during safety car periods.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session


@dataclass
class DriverState:
    """Current state of a driver during safety car period"""

    driver_id: str
    position: int
    tyre_age: int
    compound: str
    gap_to_leader: float  # seconds
    gap_to_next: float  # seconds behind car ahead


@dataclass
class SafetyCarDecision:
    """Decision recommendation for a specific driver"""

    driver_id: str
    current_position: int
    recommendation: str  # "PIT", "STAY_OUT", "RISKY"
    predicted_position_if_pit: int
    predicted_position_if_stay: int
    position_gain_if_pit: int
    position_loss_if_pit: int
    tyre_advantage: int  # laps fresher than average
    confidence: float  # 0-1
    reasoning: str


@dataclass
class SafetyCarAnalysis:
    """Complete safety car scenario analysis"""

    safety_car_lap: int
    laps_remaining: int
    drivers_who_should_pit: List[str]
    drivers_who_should_stay: List[str]
    decisions: List[SafetyCarDecision]
    field_summary: Dict[str, any]


class SafetyCarStrategyService:
    """
    Service for analyzing safety car scenarios and recommending pit strategies.

    Key Considerations:
    1. Pit loss during safety car is ~18-20s (less than normal ~22s)
    2. Field bunches up, reducing gaps
    3. Tire advantage becomes crucial for restart
    4. Position during safety car vs. after restart
    5. Remaining race distance matters
    """

    # Constants
    SC_PIT_LOSS_TIME = 18.0  # Reduced pit loss under safety car (seconds)
    NORMAL_PIT_LOSS_TIME = 22.0
    SC_LAP_TIME = 110.0  # Typical safety car lap time (seconds)
    TYRE_WARM_UP_LAPS = 2  # Laps to reach optimal temperature
    TYRE_WARM_UP_PENALTY = 0.5  # Seconds slower per warm-up lap

    def __init__(self, db: Session):
        self.db = db

    def analyze_safety_car_scenario(
        self,
        session_id: str,
        safety_car_lap: int,
        total_laps: int,
        driver_states: List[DriverState],
        track_status: str = "SC",
    ) -> SafetyCarAnalysis:
        """
        Analyze a safety car scenario and recommend pit strategies for all drivers.

        Args:
            session_id: Session identifier
            safety_car_lap: Lap when safety car was deployed
            total_laps: Total race laps
            driver_states: Current state of all drivers
            track_status: Track status (SC or VSC)

        Returns:
            Complete safety car analysis with recommendations
        """
        laps_remaining = total_laps - safety_car_lap
        decisions = []
        drivers_who_should_pit = []
        drivers_who_should_stay = []

        # Calculate field average tire age
        avg_tyre_age = sum(d.tyre_age for d in driver_states) / len(driver_states)

        # Sort drivers by position
        sorted_drivers = sorted(driver_states, key=lambda d: d.position)

        # Analyze each driver's decision
        for driver in sorted_drivers:
            decision = self._analyze_driver_decision(
                session_id=session_id,
                driver=driver,
                all_drivers=sorted_drivers,
                laps_remaining=laps_remaining,
                avg_tyre_age=avg_tyre_age,
                track_status=track_status,
            )

            decisions.append(decision)

            if decision.recommendation == "PIT":
                drivers_who_should_pit.append(driver.driver_id)
            elif decision.recommendation == "STAY_OUT":
                drivers_who_should_stay.append(driver.driver_id)

        # Calculate field summary
        field_summary = {
            "total_drivers": len(driver_states),
            "avg_tyre_age": avg_tyre_age,
            "drivers_on_old_tyres": sum(
                1 for d in driver_states if d.tyre_age > avg_tyre_age + 5
            ),
            "drivers_on_fresh_tyres": sum(
                1 for d in driver_states if d.tyre_age < 5
            ),
            "pit_window_advantage": self.SC_PIT_LOSS_TIME < self.NORMAL_PIT_LOSS_TIME,
            "laps_remaining": laps_remaining,
        }

        return SafetyCarAnalysis(
            safety_car_lap=safety_car_lap,
            laps_remaining=laps_remaining,
            drivers_who_should_pit=drivers_who_should_pit,
            drivers_who_should_stay=drivers_who_should_stay,
            decisions=decisions,
            field_summary=field_summary,
        )

    def _analyze_driver_decision(
        self,
        session_id: str,
        driver: DriverState,
        all_drivers: List[DriverState],
        laps_remaining: int,
        avg_tyre_age: float,
        track_status: str,
    ) -> SafetyCarDecision:
        """
        Analyze pit/stay decision for a specific driver.

        Strategy Logic:
        1. Count how many cars ahead will pit
        2. Count how many cars behind will pit
        3. Calculate position if pit vs. stay
        4. Consider tire age vs. field average
        5. Account for remaining race distance
        """
        current_pos = driver.position

        # Simulate if driver pits
        (
            pos_if_pit,
            pos_if_stay,
            drivers_ahead_pitting,
            drivers_behind_staying,
        ) = self._simulate_positions(driver, all_drivers, avg_tyre_age)

        # Calculate position changes
        position_gain_if_pit = max(0, current_pos - pos_if_pit)
        position_loss_if_pit = max(0, pos_if_pit - current_pos)

        # Calculate tire advantage if pit
        new_tyre_age = 0  # Fresh tires
        tyre_advantage = int(avg_tyre_age - new_tyre_age)

        # Decision logic
        recommendation, confidence, reasoning = self._make_recommendation(
            driver=driver,
            pos_if_pit=pos_if_pit,
            pos_if_stay=pos_if_stay,
            tyre_advantage=tyre_advantage,
            laps_remaining=laps_remaining,
            avg_tyre_age=avg_tyre_age,
            drivers_ahead_pitting=drivers_ahead_pitting,
        )

        return SafetyCarDecision(
            driver_id=driver.driver_id,
            current_position=current_pos,
            recommendation=recommendation,
            predicted_position_if_pit=pos_if_pit,
            predicted_position_if_stay=pos_if_stay,
            position_gain_if_pit=position_gain_if_pit,
            position_loss_if_pit=position_loss_if_pit,
            tyre_advantage=tyre_advantage,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _simulate_positions(
        self,
        driver: DriverState,
        all_drivers: List[DriverState],
        avg_tyre_age: float,
    ) -> tuple[int, int, int, int]:
        """
        Simulate field positions if driver pits vs. stays out.

        Returns:
            (position_if_pit, position_if_stay, drivers_ahead_pitting, drivers_behind_staying)
        """
        # Heuristic: drivers with old tires (>avg+5) will likely pit
        # drivers with fresh tires (<5 laps) will likely stay
        drivers_ahead = [d for d in all_drivers if d.position < driver.position]
        drivers_behind = [d for d in all_drivers if d.position > driver.position]

        # Estimate who will pit (conservative estimate)
        drivers_ahead_pitting = sum(
            1
            for d in drivers_ahead
            if d.tyre_age > avg_tyre_age + 5 or d.tyre_age > 20
        )
        drivers_behind_staying = sum(
            1 for d in drivers_behind if d.tyre_age < 5
        )

        # If driver pits:
        # - Lose positions to cars ahead who stay (drop behind them)
        # - Gain positions from cars ahead who also pit (maintain position)
        # - Gain positions from cars behind who pit (they drop behind)
        cars_ahead_staying = len(drivers_ahead) - drivers_ahead_pitting

        # Conservative position estimate if pit
        pos_if_pit = driver.position + cars_ahead_staying

        # If driver stays:
        # - Keep current position
        # - But might lose to cars behind with fresher tires later
        pos_if_stay = driver.position

        return pos_if_pit, pos_if_stay, drivers_ahead_pitting, drivers_behind_staying

    def _make_recommendation(
        self,
        driver: DriverState,
        pos_if_pit: int,
        pos_if_stay: int,
        tyre_advantage: int,
        laps_remaining: int,
        avg_tyre_age: float,
        drivers_ahead_pitting: int,
    ) -> tuple[str, float, str]:
        """
        Make final pit/stay recommendation based on all factors.

        Returns:
            (recommendation, confidence, reasoning)
        """
        # Factor 1: Tire age vs. field average
        tyre_delta = driver.tyre_age - avg_tyre_age

        # Factor 2: Remaining race distance
        # More laps = tire advantage matters more
        distance_factor = min(1.0, laps_remaining / 30.0)

        # Factor 3: Position delta
        position_delta = pos_if_pit - pos_if_stay

        # Decision matrix
        reasons = []

        # Strong pit signals
        if driver.tyre_age > 20:
            reasons.append("Tires critically old (>20 laps)")
        if driver.tyre_age > avg_tyre_age + 8:
            reasons.append(f"Tires much older than field avg (+{int(tyre_delta)} laps)")
        if laps_remaining > 15 and tyre_advantage > 10:
            reasons.append(f"Long race remaining ({laps_remaining} laps) - tire advantage crucial")
        if position_delta <= 2 and driver.tyre_age > 15:
            reasons.append(f"Minimal position loss ({position_delta}) with tire refresh")

        # Strong stay signals
        if driver.tyre_age < 5:
            reasons.append("Tires very fresh (<5 laps)")
        if position_delta > 5:
            reasons.append(f"Large position loss if pit (-{position_delta} positions)")
        if laps_remaining < 10:
            reasons.append(f"Short race remaining ({laps_remaining} laps)")
        if driver.position <= 3 and driver.tyre_age < 15:
            reasons.append("Leading position with acceptable tire age")

        # Calculate confidence
        if driver.tyre_age > 20 or (tyre_delta > 10 and laps_remaining > 15):
            recommendation = "PIT"
            confidence = min(0.95, 0.7 + (tyre_delta / 30.0) + (laps_remaining / 60.0))
            reasoning = " | ".join(reasons) if reasons else "Old tires, good opportunity to pit"

        elif driver.tyre_age < 5 or position_delta > 5 or laps_remaining < 8:
            recommendation = "STAY_OUT"
            confidence = min(0.95, 0.7 + (1.0 - tyre_delta / 30.0))
            reasoning = (
                " | ".join(reasons)
                if reasons
                else "Fresh tires or unfavorable position trade"
            )

        else:
            # Borderline case
            recommendation = "RISKY"
            confidence = 0.5
            reasoning = f"Borderline: {int(tyre_delta)} laps vs avg, {laps_remaining} laps remaining, {position_delta} position change"

        return recommendation, confidence, reasoning

    def calculate_optimal_compound(
        self,
        current_compound: str,
        tyre_age: int,
        laps_remaining: int,
        temperature: float = 30.0,
    ) -> str:
        """
        Recommend optimal tire compound for safety car pit stop.

        Args:
            current_compound: Current tire compound
            tyre_age: Current tire age
            laps_remaining: Laps remaining in race
            temperature: Track temperature

        Returns:
            Recommended compound
        """
        # Simple heuristic for compound selection
        if laps_remaining > 25:
            # Long stint - prefer harder compound
            if temperature > 35:
                return "MEDIUM"  # Hot track
            else:
                return "HARD"  # Cooler track
        elif laps_remaining > 15:
            # Medium stint - medium compound
            return "MEDIUM"
        else:
            # Short sprint to finish - softest compound
            return "SOFT"
