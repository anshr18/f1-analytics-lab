/**
 * Prediction Types
 *
 * TypeScript interfaces for ML predictions and models.
 */

export interface Model {
  id: string;
  model_name: string;
  version: string;
  model_type: string;
  status: string;
  metrics: Record<string, number>;
  artifact_path: string;
  created_at: string;
  updated_at: string;
}

export interface PredictionRequest {
  model_name: string;
  version: string;
  input_data: Record<string, any>;
}

export interface PredictionResult {
  prediction_id?: string;
  model_name: string;
  version: string;
  prediction_value: any;
  confidence?: Record<string, number>;
}

export interface TyreDegradationPrediction {
  stint_id: string;
  predicted_deg_per_lap: number;
  compound: string;
  driver_id: string;
  model_version: string;
}

export interface LapTimePrediction {
  predicted_lap_time: number;
  tyre_age: number;
  compound: string;
  track_status: string;
  position: number;
  driver_id: string;
  model_version: string;
}

export interface OvertakePrediction {
  overtake_probability: number;
  gap_seconds: number;
  closing_rate: number;
  tyre_advantage: number;
  drs_available: boolean;
  lap_number: number;
  model_version: string;
}

export interface RaceResultPrediction {
  predicted_position: number;
  top3_probabilities: Record<number, number>;
  grid_position: number;
  avg_lap_time: number;
  driver_id: string;
  model_version: string;
}

export type PredictionResponse =
  | TyreDegradationPrediction
  | LapTimePrediction
  | OvertakePrediction
  | RaceResultPrediction;
