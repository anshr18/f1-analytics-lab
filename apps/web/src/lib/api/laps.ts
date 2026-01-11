/**
 * F1 Intelligence Hub - Laps API
 *
 * API functions for lap timing data.
 */

import { apiGet } from "./client";
import type { Lap, LapListResponse } from "@/types/api";

export async function fetchLaps(sessionId: string, driverId?: string): Promise<Lap[]> {
  const response = await apiGet<LapListResponse>("/laps", {
    session_id: sessionId,
    driver_id: driverId,
    limit: 1000, // Get all laps
  });
  return response.laps;
}
