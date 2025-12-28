"use client";

import { Card } from "@/components/ui/Card";
import type {
  TyreDegradationPrediction,
  LapTimePrediction,
  OvertakePrediction,
  RaceResultPrediction,
} from "@/types/predictions";

interface PredictionResultsProps {
  modelName: string;
  result:
    | TyreDegradationPrediction
    | LapTimePrediction
    | OvertakePrediction
    | RaceResultPrediction
    | null;
}

export function PredictionResults({
  modelName,
  result,
}: PredictionResultsProps) {
  if (!result) {
    return null;
  }

  const renderTyreDegradation = (data: TyreDegradationPrediction) => (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          Predicted Degradation Rate
        </h3>
        <p className="text-5xl font-bold text-red-600">
          {data.predicted_deg_per_lap.toFixed(4)}
        </p>
        <p className="text-gray-500 mt-1">seconds/lap</p>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs text-gray-500">Compound</p>
          <p className="font-semibold">{data.compound}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Driver</p>
          <p className="font-semibold">{data.driver_id}</p>
        </div>
      </div>
    </div>
  );

  const renderLapTime = (data: LapTimePrediction) => (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          Predicted Lap Time
        </h3>
        <p className="text-5xl font-bold text-red-600">
          {data.predicted_lap_time.toFixed(3)}s
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs text-gray-500">Tyre Age</p>
          <p className="font-semibold">{data.tyre_age} laps</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Compound</p>
          <p className="font-semibold">{data.compound}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Track Status</p>
          <p className="font-semibold">{data.track_status}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Position</p>
          <p className="font-semibold">P{data.position}</p>
        </div>
      </div>
    </div>
  );

  const renderOvertake = (data: OvertakePrediction) => (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          Overtake Probability
        </h3>
        <p className="text-5xl font-bold text-red-600">
          {(data.overtake_probability * 100).toFixed(1)}%
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs text-gray-500">Gap</p>
          <p className="font-semibold">{data.gap_seconds.toFixed(3)}s</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Closing Rate</p>
          <p className="font-semibold">{data.closing_rate.toFixed(3)}s/lap</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Tyre Advantage</p>
          <p className="font-semibold">
            {data.tyre_advantage > 0 ? "+" : ""}
            {data.tyre_advantage}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">DRS</p>
          <p className="font-semibold">
            {data.drs_available ? "Available" : "Not Available"}
          </p>
        </div>
      </div>
    </div>
  );

  const renderRaceResult = (data: RaceResultPrediction) => (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          Predicted Finish Position
        </h3>
        <p className="text-5xl font-bold text-red-600">
          P{data.predicted_position}
        </p>
      </div>
      <div className="pt-4 border-t">
        <h4 className="text-xs font-medium text-gray-600 mb-2">
          Position Probabilities (±1)
        </h4>
        <div className="space-y-2">
          {Object.entries(data.top3_probabilities)
            .sort(([a], [b]) => Number(a) - Number(b))
            .map(([position, probability]) => (
              <div key={position} className="flex items-center gap-2">
                <span className="text-sm font-medium w-8">P{position}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-red-600 h-4 rounded-full transition-all"
                    style={{ width: `${probability * 100}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600 w-12 text-right">
                  {(probability * 100).toFixed(0)}%
                </span>
              </div>
            ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs text-gray-500">Grid Position</p>
          <p className="font-semibold">P{data.grid_position}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Driver</p>
          <p className="font-semibold">{data.driver_id}</p>
        </div>
      </div>
    </div>
  );

  return (
    <Card title="Prediction Result">
      {modelName === "tyre_degradation" &&
        renderTyreDegradation(result as TyreDegradationPrediction)}
      {modelName === "lap_time" && renderLapTime(result as LapTimePrediction)}
      {modelName === "overtake" && renderOvertake(result as OvertakePrediction)}
      {modelName === "race_result" &&
        renderRaceResult(result as RaceResultPrediction)}
      <div className="mt-4 pt-4 border-t text-xs text-gray-500 text-center">
        Model: {modelName} v
        {"model_version" in result ? result.model_version : "unknown"}
      </div>
    </Card>
  );
}
