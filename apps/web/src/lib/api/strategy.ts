/**
 * Strategy API Client
 *
 * Functions for interacting with race strategy simulation endpoints.
 */

import { apiPost } from "./client";
import type {
  UndercutRequest,
  UndercutResponse,
  SafetyCarRequest,
  SafetyCarResponse,
  RaceSimulationRequest,
  RaceSimulationResponse,
} from "@/types/strategy";

/**
 * Calculate optimal undercut/overcut strategy
 */
export async function calculateUndercut(
  request: UndercutRequest
): Promise<UndercutResponse> {
  return apiPost<UndercutResponse>("/strategy/undercut", request);
}

/**
 * Analyze safety car scenario and get pit/stay recommendations
 */
export async function analyzeSafetyCar(
  request: SafetyCarRequest
): Promise<SafetyCarResponse> {
  return apiPost<SafetyCarResponse>("/strategy/safety-car", request);
}

/**
 * Simulate complete race with pit strategies
 */
export async function simulateRace(
  request: RaceSimulationRequest
): Promise<RaceSimulationResponse> {
  return apiPost<RaceSimulationResponse>("/strategy/race-simulation", request);
}
