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
