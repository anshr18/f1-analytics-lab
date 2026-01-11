/**
 * F1 Intelligence Hub - Stints API
 *
 * API functions for tyre stint data.
 */

import { apiGet } from "./client";
import type { Stint, StintListResponse } from "@/types/api";

export async function fetchStints(sessionId: string, driverId?: string): Promise<Stint[]> {
  const response = await apiGet<StintListResponse>("/stints", {
    session_id: sessionId,
    driver_id: driverId,
  });
  return response.stints;
}
