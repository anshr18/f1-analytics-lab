"use client";

import { useState } from "react";
import {
  predictTyreDegradation,
  predictLapTime,
  predictOvertake,
  predictRaceResult,
} from "@/lib/api/predictions";
import type { PredictionResponse } from "@/types/predictions";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface PredictionFormProps {
  modelName: string;
  onPredict: (result: PredictionResponse) => void;
}

export function PredictionForm({ modelName, onPredict }: PredictionFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state for different models
  const [stintId, setStintId] = useState("");
  const [tyreAge, setTyreAge] = useState(10);
  const [compound, setCompound] = useState("SOFT");
  const [trackStatus, setTrackStatus] = useState("GREEN");
  const [position, setPosition] = useState(5);
  const [driverId, setDriverId] = useState("VER");
  const [gapSeconds, setGapSeconds] = useState(1.2);
  const [closingRate, setClosingRate] = useState(-0.1);
  const [tyreAdvantage, setTyreAdvantage] = useState(0);
  const [drsAvailable, setDrsAvailable] = useState(true);
  const [lapNumber, setLapNumber] = useState(30);
  const [gridPosition, setGridPosition] = useState(3);
  const [avgLapTime, setAvgLapTime] = useState(92.5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let result: PredictionResponse;

      switch (modelName) {
        case "tyre_degradation":
          result = await predictTyreDegradation(stintId);
          break;

        case "lap_time":
          result = await predictLapTime({
            tyre_age: tyreAge,
            compound,
            track_status: trackStatus,
            position,
            driver_id: driverId,
          });
          break;

        case "overtake":
          result = await predictOvertake({
            gap_seconds: gapSeconds,
            closing_rate: closingRate,
            tyre_advantage: tyreAdvantage,
            drs_available: drsAvailable,
            lap_number: lapNumber,
          });
          break;

        case "race_result":
          result = await predictRaceResult({
            grid_position: gridPosition,
            avg_lap_time: avgLapTime,
            driver_id: driverId,
          });
          break;

        default:
          throw new Error("Unknown model type");
      }

      onPredict(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const renderTyreDegradationForm = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Stint ID
        </label>
        <input
          type="text"
          value={stintId}
          onChange={(e) => setStintId(e.target.value)}
          placeholder="e.g., 01234567-89ab-cdef-0123-456789abcdef"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          UUID of the stint to predict degradation for
        </p>
      </div>
    </div>
  );

  const renderLapTimeForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tyre Age (laps)
          </label>
          <input
            type="number"
            value={tyreAge}
            onChange={(e) => setTyreAge(Number(e.target.value))}
            min="0"
            max="50"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Compound
          </label>
          <select
            value={compound}
            onChange={(e) => setCompound(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          >
            <option value="SOFT">SOFT</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HARD">HARD</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Track Status
          </label>
          <select
            value={trackStatus}
            onChange={(e) => setTrackStatus(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          >
            <option value="GREEN">GREEN</option>
            <option value="YELLOW">YELLOW</option>
            <option value="SC">SC (Safety Car)</option>
            <option value="VSC">VSC (Virtual SC)</option>
            <option value="RED">RED</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Position
          </label>
          <input
            type="number"
            value={position}
            onChange={(e) => setPosition(Number(e.target.value))}
            min="1"
            max="20"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Driver ID
        </label>
        <input
          type="text"
          value={driverId}
          onChange={(e) => setDriverId(e.target.value)}
          placeholder="e.g., VER, HAM, LEC"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          required
        />
      </div>
    </div>
  );

  const renderOvertakeForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Gap (seconds)
          </label>
          <input
            type="number"
            value={gapSeconds}
            onChange={(e) => setGapSeconds(Number(e.target.value))}
            step="0.1"
            min="0"
            max="5"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Closing Rate (s/lap)
          </label>
          <input
            type="number"
            value={closingRate}
            onChange={(e) => setClosingRate(Number(e.target.value))}
            step="0.05"
            min="-2"
            max="2"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Negative = closing, positive = opening
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tyre Advantage
          </label>
          <select
            value={tyreAdvantage}
            onChange={(e) => setTyreAdvantage(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          >
            <option value={-2}>-2 (Much slower compound)</option>
            <option value={-1}>-1 (Slower compound)</option>
            <option value={0}>0 (Same compound)</option>
            <option value={1}>+1 (Faster compound)</option>
            <option value={2}>+2 (Much faster compound)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Lap Number
          </label>
          <input
            type="number"
            value={lapNumber}
            onChange={(e) => setLapNumber(Number(e.target.value))}
            min="1"
            max="70"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
      </div>
      <div>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={drsAvailable}
            onChange={(e) => setDrsAvailable(e.target.checked)}
            className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
          />
          <span className="text-sm font-medium text-gray-700">
            DRS Available
          </span>
        </label>
      </div>
    </div>
  );

  const renderRaceResultForm = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Grid Position
          </label>
          <input
            type="number"
            value={gridPosition}
            onChange={(e) => setGridPosition(Number(e.target.value))}
            min="1"
            max="20"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Avg Lap Time (seconds)
          </label>
          <input
            type="number"
            value={avgLapTime}
            onChange={(e) => setAvgLapTime(Number(e.target.value))}
            step="0.1"
            min="80"
            max="120"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            required
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Driver ID
        </label>
        <input
          type="text"
          value={driverId}
          onChange={(e) => setDriverId(e.target.value)}
          placeholder="e.g., VER, HAM, LEC"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          required
        />
      </div>
    </div>
  );

  return (
    <Card title="Prediction Input">
      <form onSubmit={handleSubmit}>
        {modelName === "tyre_degradation" && renderTyreDegradationForm()}
        {modelName === "lap_time" && renderLapTimeForm()}
        {modelName === "overtake" && renderOvertakeForm()}
        {modelName === "race_result" && renderRaceResultForm()}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="mt-6">
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Predicting..." : "Make Prediction"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
