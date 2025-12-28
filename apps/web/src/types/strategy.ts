/**
 * Strategy Types
 *
 * TypeScript interfaces for race strategy simulation and undercut calculations.
 */

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
