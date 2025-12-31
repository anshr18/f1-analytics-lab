/**
 * Strategy Types
 *
 * TypeScript interfaces for race strategy simulation and undercut calculations.
 */

// Undercut/Overcut Types

/**
 * Lap-by-lap detail for strategy simulation
 */
export interface LapDetail {
  lap: number;
  attacker_lap_time: number;
  defender_lap_time: number;
  lap_delta: number;
  cumulative_gap: number;
  attacker_tyre_age: number;
  defender_tyre_age: number;
  attacker_position: number;
  defender_position: number;
}

/**
 * Request for undercut/overcut calculation
 */
export interface UndercutRequest {
  session_id: string;
  attacking_driver: string;
  defending_driver: string;
  current_lap: number;
  gap_seconds: number;
  tyre_age_attacker: number;
  tyre_age_defender: number;
  attacker_compound?: string;
  defender_compound?: string;
  track_status?: string;
}

/**
 * Response from undercut/overcut calculation
 */
export interface UndercutResponse {
  time_delta: number;
  optimal_pit_lap: number;
  success_probability: number;
  attacker_outlap: number;
  defender_response_lap: number;
  net_positions: Record<string, number>;
  lap_by_lap: LapDetail[];
}

// Safety Car Strategy Types

/**
 * Current state of a driver during safety car period
 */
export interface DriverStateInput {
  driver_id: string;
  position: number;
  tyre_age: number;
  compound: string;
  gap_to_leader: number;
  gap_to_next: number;
}

/**
 * Request for safety car strategy analysis
 */
export interface SafetyCarRequest {
  session_id: string;
  safety_car_lap: number;
  total_laps: number;
  driver_states: DriverStateInput[];
  track_status?: string;
}

/**
 * Decision recommendation for a specific driver
 */
export interface SafetyCarDecision {
  driver_id: string;
  current_position: number;
  recommendation: "PIT" | "STAY_OUT" | "RISKY";
  predicted_position_if_pit: number;
  predicted_position_if_stay: number;
  position_gain_if_pit: number;
  position_loss_if_pit: number;
  tyre_advantage: number;
  confidence: number;
  reasoning: string;
}

/**
 * Response from safety car strategy analysis
 */
export interface SafetyCarResponse {
  safety_car_lap: number;
  laps_remaining: number;
  drivers_who_should_pit: string[];
  drivers_who_should_stay: string[];
  decisions: SafetyCarDecision[];
  field_summary: {
    total_drivers: number;
    avg_tyre_age: number;
    drivers_on_old_tyres: number;
    drivers_on_fresh_tyres: number;
    pit_window_advantage: boolean;
    laps_remaining: number;
  };
}

// Race Simulation Types

/**
 * Request for complete race simulation
 */
export interface RaceSimulationRequest {
  session_id: string;
  total_laps: number;
  drivers: string[];
  pit_strategies: Record<string, number[]>;
}

/**
 * Response from race simulation
 */
export interface RaceSimulationResponse {
  final_classification: Record<string, number>;
  lap_by_lap_positions: Record<string, number>[];
  total_pit_stops: Record<string, number>;
  fastest_lap: {
    driver: string;
    lap: number;
    time?: number;
  };
  summary: string;
}
