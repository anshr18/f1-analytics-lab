"use client";

import { useEffect, useState } from "react";
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
    const fetch = async () => {
      try {
        setLoading(true);
        setError(null);
        let result;
        switch (modelName) {
          case "lap_time":
            result = await predictLapTime({ tyre_age: 15, compound: "MEDIUM", track_status: "GREEN", position: 1, driver_id: "VER" });
            break;
          case "overtake":
            result = await predictOvertake({ gap_seconds: 1.5, closing_rate: -0.15, tyre_advantage: 1, drs_available: true, lap_number: 35 });
            break;
          case "race_result":
            result = await predictRaceResult({ grid_position: 1, avg_lap_time: 91.5, driver_id: "VER" });
            break;
        }
        setPrediction(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed");
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [sessionId, modelName]);

  const getValue = () => {
    if (loading) return <span className="text-surface-container-highest animate-pulse">···</span>;
    if (error) return <span className="text-error font-data-sm text-data-sm">Error</span>;
    if (!prediction) return <span className="text-surface-container-highest">—</span>;

    switch (modelName) {
      case "lap_time": {
        const d = prediction as LapTimePrediction;
        const secs = d.predicted_lap_time;
        const m = Math.floor(secs / 60);
        const s = (secs % 60).toFixed(3).padStart(6, "0");
        return <>{m}:{s}</>;
      }
      case "overtake": {
        const d = prediction as OvertakePrediction;
        return <>{(d.overtake_probability * 100).toFixed(0)}%</>;
      }
      case "race_result": {
        const d = prediction as RaceResultPrediction;
        return <>P{d.predicted_position}</>;
      }
    }
  };

  return (
    <div className="bg-[#141414] border border-[#2A2A2A] border-l-2 border-l-primary-container p-md flex flex-col gap-xs">
      <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
        {title}
      </span>
      <div className="font-data-lg text-data-lg text-on-surface mt-xs">
        {getValue()}
      </div>
    </div>
  );
}
