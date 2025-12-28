"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import {
  predictLapTime,
  predictOvertake,
  predictRaceResult,
} from "@/lib/api/predictions";
import type {
  LapTimePrediction,
  OvertakePrediction,
  RaceResultPrediction,
} from "@/types/predictions";

interface PredictionSummaryCardProps {
  title: string;
  modelName: "lap_time" | "overtake" | "race_result";
  sessionId?: string;
}

export function PredictionSummaryCard({
  title,
  modelName,
  sessionId,
}: PredictionSummaryCardProps) {
  const [prediction, setPrediction] = useState<
    LapTimePrediction | OvertakePrediction | RaceResultPrediction | null
  >(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const fetchPrediction = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use default/example parameters for each model
        let result;
        switch (modelName) {
          case "lap_time":
            result = await predictLapTime({
              tyre_age: 15,
              compound: "MEDIUM",
              track_status: "GREEN",
              position: 1,
              driver_id: "VER",
            });
            break;

          case "overtake":
            result = await predictOvertake({
              gap_seconds: 1.5,
              closing_rate: -0.15,
              tyre_advantage: 1,
              drs_available: true,
              lap_number: 35,
            });
            break;

          case "race_result":
            result = await predictRaceResult({
              grid_position: 1,
              avg_lap_time: 91.5,
              driver_id: "VER",
            });
            break;
        }

        setPrediction(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Prediction failed");
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [sessionId, modelName]);

  const renderContent = () => {
    if (loading) {
      return (
        <div className="text-center py-4 text-gray-500 text-sm">
          Loading...
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-4 text-red-500 text-sm">{error}</div>
      );
    }

    if (!prediction) {
      return (
        <div className="text-center py-4 text-gray-400 text-sm">
          Select a session to see predictions
        </div>
      );
    }

    switch (modelName) {
      case "lap_time": {
        const data = prediction as LapTimePrediction;
        return (
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {data.predicted_lap_time.toFixed(2)}s
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Leader pace (15 laps on mediums)
            </div>
          </div>
        );
      }

      case "overtake": {
        const data = prediction as OvertakePrediction;
        return (
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {(data.overtake_probability * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Battle probability (1.5s gap, DRS)
            </div>
          </div>
        );
      }

      case "race_result": {
        const data = prediction as RaceResultPrediction;
        return (
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              P{data.predicted_position}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Expected finish from pole
            </div>
          </div>
        );
      }
    }
  };

  return (
    <Card title={title}>
      <div className="py-2">{renderContent()}</div>
    </Card>
  );
}
