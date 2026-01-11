"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { fetchLaps } from "@/lib/api/laps";
import { durationToSeconds, formatLapTime } from "@/lib/api/client";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import type { Lap } from "@/types/api";

interface LapChartProps {
  sessionId: string;
}

// Driver colors for the chart
const DRIVER_COLORS: Record<string, string> = {
  ver: "#0600EF", // Verstappen - Blue
  per: "#0600EF",
  lec: "#DC0000", // Ferrari - Red
  sai: "#DC0000",
  ham: "#00D2BE", // Mercedes - Teal
  rus: "#00D2BE",
  nor: "#FF8700", // McLaren - Orange
  pia: "#FF8700",
  alo: "#006F62", // Aston Martin - Green
  str: "#006F62",
  // Add more as needed
};

export function LapChart({ sessionId }: LapChartProps) {
  const [chartData, setChartData] = useState<any[]>([]);
  const [drivers, setDrivers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLapData();
  }, [sessionId]);

  async function loadLapData() {
    try {
      setLoading(true);
      setError(null);

      const laps = await fetchLaps(sessionId);

      // Filter out deleted laps and pit laps
      const validLaps = laps.filter((lap) => !lap.deleted && !lap.is_pit_out_lap && !lap.is_pit_in_lap && lap.lap_time);

      // Get unique drivers
      const uniqueDrivers = Array.from(new Set(validLaps.map((lap) => lap.driver_id)));
      setDrivers(uniqueDrivers);

      // Group by lap number
      const lapGroups: Record<number, Record<string, number>> = {};

      validLaps.forEach((lap) => {
        const lapTime = durationToSeconds(lap.lap_time);
        if (lapTime === null || lapTime <= 0) return;

        if (!lapGroups[lap.lap_number]) {
          lapGroups[lap.lap_number] = {};
        }

        lapGroups[lap.lap_number][lap.driver_id] = lapTime;
      });

      // Convert to chart data format
      const data = Object.entries(lapGroups)
        .map(([lapNum, drivers]) => ({
          lap: Number(lapNum),
          ...drivers,
        }))
        .sort((a, b) => a.lap - b.lap);

      setChartData(data);
    } catch (err: any) {
      setError(err.message || "Failed to load lap data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <Card title="Lap Time Evolution">
        <div className="h-96 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Lap Time Evolution">
        <div className="h-96 flex items-center justify-center text-red-500">{error}</div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card title="Lap Time Evolution">
        <div className="h-96 flex items-center justify-center text-gray-500">No lap data available</div>
      </Card>
    );
  }

  return (
    <Card title="Lap Time Evolution">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="lap" label={{ value: "Lap Number", position: "insideBottom", offset: -5 }} />
          <YAxis
            label={{ value: "Lap Time (seconds)", angle: -90, position: "insideLeft" }}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151" }}
            formatter={(value: number) => formatLapTime(value)}
          />
          <Legend />
          {drivers.map((driver, index) => (
            <Line
              key={driver}
              type="monotone"
              dataKey={driver}
              stroke={DRIVER_COLORS[driver] || `hsl(${(index * 360) / drivers.length}, 70%, 50%)`}
              name={driver.toUpperCase()}
              dot={false}
              strokeWidth={2}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
