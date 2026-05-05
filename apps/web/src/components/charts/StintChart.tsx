"use client";

import { useEffect, useState } from "react";
import { fetchStints } from "@/lib/api/stints";
import { Card, CardHeader } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

interface StintChartProps {
  sessionId: string;
}

interface DriverStint {
  stint_number: number;
  compound: string;
  lap_start: number;
  lap_end: number;
  total_laps: number;
}

interface DriverData {
  driver: string;
  stints: DriverStint[];
}

// Tyre compound colors (official F1 colors)
const COMPOUND_COLORS: Record<string, string> = {
  SOFT: "#DA291C", // Red
  MEDIUM: "#FFF200", // Yellow
  HARD: "#F0F0F0", // White
  INTERMEDIATE: "#43B02A", // Green
  WET: "#0067AD", // Blue
};

export function StintChart({ sessionId }: StintChartProps) {
  const [chartData, setChartData] = useState<DriverData[]>([]);
  const [maxLap, setMaxLap] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredStint, setHoveredStint] = useState<{
    driver: string;
    stint: DriverStint;
  } | null>(null);

  useEffect(() => {
    loadStintData();
  }, [sessionId]);

  async function loadStintData() {
    try {
      setLoading(true);
      setError(null);

      const stints = await fetchStints(sessionId);

      // Group stints by driver
      const driverStints: Record<string, DriverStint[]> = {};
      let maxLapEnd = 0;

      stints.forEach((stint) => {
        if (!driverStints[stint.driver_id]) {
          driverStints[stint.driver_id] = [];
        }

        const lapEnd = stint.lap_end || stint.lap_start || 1;
        if (lapEnd > maxLapEnd) maxLapEnd = lapEnd;

        driverStints[stint.driver_id].push({
          stint_number: stint.stint_number,
          compound: stint.compound,
          lap_start: stint.lap_start || 1,
          lap_end: lapEnd,
          total_laps: stint.total_laps || 1,
        });
      });

      // Convert to array format sorted by driver
      const data: DriverData[] = Object.entries(driverStints)
        .map(([driverId, stints]) => ({
          driver: driverId.toUpperCase(),
          stints: stints.sort((a, b) => a.lap_start - b.lap_start),
        }))
        .sort((a, b) => a.driver.localeCompare(b.driver));

      setChartData(data);
      setMaxLap(maxLapEnd);
    } catch (err: any) {
      setError(err.message || "Failed to load stint data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader title="Tyre Strategy" />
        <div className="h-96 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader title="Tyre Strategy" />
        <div className="h-96 flex items-center justify-center text-red-500">
          {error}
        </div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card>
        <CardHeader title="Tyre Strategy" />
        <div className="h-96 flex items-center justify-center text-gray-500">
          No stint data available
        </div>
      </Card>
    );
  }

  const barHeight = 20;
  const barGap = 4;
  const leftPadding = 60;
  const rightPadding = 20;
  const topPadding = 10;
  const bottomPadding = 30;
  const chartHeight = chartData.length * (barHeight + barGap) + topPadding + bottomPadding;

  return (
    <Card>
      <CardHeader title="Tyre Strategy" />
      <div className="mb-4">
        <div className="flex flex-wrap gap-4 text-sm">
          {Object.entries(COMPOUND_COLORS).map(([compound, color]) => (
            <div key={compound} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded border border-gray-400"
                style={{ backgroundColor: color }}
              />
              <span>{compound}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <svg
          width="100%"
          height={chartHeight}
          viewBox={`0 0 800 ${chartHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* X-axis labels */}
          {[0, Math.floor(maxLap / 4), Math.floor(maxLap / 2), Math.floor((3 * maxLap) / 4), maxLap].map(
            (lap, i) => (
              <text
                key={i}
                x={leftPadding + ((800 - leftPadding - rightPadding) * lap) / maxLap}
                y={chartHeight - 10}
                textAnchor="middle"
                className="fill-gray-400 text-xs"
              >
                {lap}
              </text>
            )
          )}

          {/* X-axis title */}
          <text
            x={400}
            y={chartHeight - 2}
            textAnchor="middle"
            className="fill-gray-500 text-xs"
          >
            Lap
          </text>

          {/* Driver rows */}
          {chartData.map((driverData, driverIndex) => {
            const y = topPadding + driverIndex * (barHeight + barGap);

            return (
              <g key={driverData.driver}>
                {/* Driver label */}
                <text
                  x={leftPadding - 8}
                  y={y + barHeight / 2 + 4}
                  textAnchor="end"
                  className="fill-gray-300 text-xs font-medium"
                >
                  {driverData.driver}
                </text>

                {/* Background bar */}
                <rect
                  x={leftPadding}
                  y={y}
                  width={800 - leftPadding - rightPadding}
                  height={barHeight}
                  fill="#1f2937"
                  rx={2}
                />

                {/* Stint segments */}
                {driverData.stints.map((stint, stintIndex) => {
                  const chartWidth = 800 - leftPadding - rightPadding;
                  const stintX = leftPadding + ((stint.lap_start - 1) / maxLap) * chartWidth;
                  const stintWidth = ((stint.lap_end - stint.lap_start + 1) / maxLap) * chartWidth;
                  const color = COMPOUND_COLORS[stint.compound] || "#666";

                  return (
                    <rect
                      key={stintIndex}
                      x={stintX}
                      y={y}
                      width={Math.max(stintWidth, 2)}
                      height={barHeight}
                      fill={color}
                      stroke="#000"
                      strokeWidth={0.5}
                      rx={2}
                      className="cursor-pointer transition-opacity hover:opacity-80"
                      onMouseEnter={() => setHoveredStint({ driver: driverData.driver, stint })}
                      onMouseLeave={() => setHoveredStint(null)}
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Tooltip */}
      {hoveredStint && (
        <div className="mt-2 p-2 bg-gray-800 border border-gray-600 rounded text-sm inline-block">
          <span className="font-bold">{hoveredStint.driver}</span>: {hoveredStint.stint.compound} (
          Laps {hoveredStint.stint.lap_start}-{hoveredStint.stint.lap_end}, {hoveredStint.stint.total_laps} laps)
        </div>
      )}
    </Card>
  );
}
