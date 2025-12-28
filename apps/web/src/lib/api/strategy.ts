/**
 * Strategy API Client
 *
 * Functions for interacting with race strategy simulation endpoints.
 */

import { apiPost } from "./client";
import type { UndercutRequest, UndercutResponse } from "@/types/strategy";

/**
 * Calculate optimal undercut/overcut strategy
 */
export async function calculateUndercut(
  request: UndercutRequest
): Promise<UndercutResponse> {
  return apiPost<UndercutResponse>("/strategy/undercut", request);
}
