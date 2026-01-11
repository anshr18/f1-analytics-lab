/**
 * Predictions API Client
 *
 * Functions for interacting with ML prediction endpoints.
 */

import { apiGet } from "./client";
import type {
  Model,
  TyreDegradationPrediction,
  LapTimePrediction,
  OvertakePrediction,
  RaceResultPrediction,
} from "@/types/predictions";

/**
 * Fetch all registered models
 */
export async function fetchModels(
  modelName?: string,
  status?: string
): Promise<Model[]> {
  const params = new URLSearchParams();
  if (modelName) params.append("model_name", modelName);
  if (status) params.append("status", status);

  const response = await apiGet<{ models: Model[] }>(
    `/models${params.toString() ? `?${params}` : ""}`
  );
  return response.models;
}

/**
 * Fetch a specific model by ID
 */
export async function fetchModel(modelId: string): Promise<Model> {
  return apiGet<Model>(`/models/${modelId}`);
}

/**
 * Predict tyre degradation for a stint
 */
export async function predictTyreDegradation(
  stintId: string
): Promise<TyreDegradationPrediction> {
  return apiGet<TyreDegradationPrediction>(
    `/predictions/tyre-degradation/${stintId}`
  );
}

/**
 * Predict lap time for given conditions
 */
export async function predictLapTime(params: {
  tyre_age: number;
  compound: string;
  track_status: string;
  position: number;
  driver_id: string;
}): Promise<LapTimePrediction> {
  const queryParams = new URLSearchParams({
    tyre_age: params.tyre_age.toString(),
    compound: params.compound,
    track_status: params.track_status,
    position: params.position.toString(),
    driver_id: params.driver_id,
  });

  return apiGet<LapTimePrediction>(`/predictions/lap-time?${queryParams}`);
}

/**
 * Predict overtake probability
 */
export async function predictOvertake(params: {
  gap_seconds: number;
  closing_rate: number;
  tyre_advantage: number;
  drs_available: boolean;
  lap_number: number;
}): Promise<OvertakePrediction> {
  const queryParams = new URLSearchParams({
    gap_seconds: params.gap_seconds.toString(),
    closing_rate: params.closing_rate.toString(),
    tyre_advantage: params.tyre_advantage.toString(),
    drs_available: params.drs_available.toString(),
    lap_number: params.lap_number.toString(),
  });

  return apiGet<OvertakePrediction>(`/predictions/overtake?${queryParams}`);
}

/**
 * Predict race result finishing position
 */
export async function predictRaceResult(params: {
  grid_position: number;
  avg_lap_time: number;
  driver_id: string;
}): Promise<RaceResultPrediction> {
  const queryParams = new URLSearchParams({
    grid_position: params.grid_position.toString(),
    avg_lap_time: params.avg_lap_time.toString(),
    driver_id: params.driver_id,
  });

  return apiGet<RaceResultPrediction>(`/predictions/race-result?${queryParams}`);
}
