"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";
import { fetchStints } from "@/lib/api/stints";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

interface StintChartProps {
  sessionId: string;
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
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStintData();
  }, [sessionId]);

  async function loadStintData() {
    try {
      setLoading(true);
      setError(null);

      const stints = await fetchStints(sessionId);

      // Group stints by driver
      const driverStints: Record<string, any[]> = {};

      stints.forEach((stint) => {
        if (!driverStints[stint.driver_id]) {
          driverStints[stint.driver_id] = [];
        }

        driverStints[stint.driver_id].push({
          stint_number: stint.stint_number,
          compound: stint.compound,
          lap_start: stint.lap_start,
          lap_end: stint.lap_end || stint.lap_start,
          total_laps: stint.total_laps || 1,
        });
      });

      // Convert to chart format (each driver is a bar, stints are segments)
      const data = Object.entries(driverStints).map(([driverId, stints]) => {
        const stintData: Record<string, any> = {
          driver: driverId.toUpperCase(),
        };

        stints.forEach((stint) => {
          const key = `stint_${stint.stint_number}_${stint.compound}`;
          stintData[key] = {
            start: stint.lap_start,
            end: stint.lap_end,
            laps: stint.total_laps,
            compound: stint.compound,
          };
        });

        return stintData;
      });

      setChartData(data);
    } catch (err: any) {
      setError(err.message || "Failed to load stint data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <Card title="Tyre Strategy">
        <div className="h-96 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Tyre Strategy">
        <div className="h-96 flex items-center justify-center text-red-500">{error}</div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card title="Tyre Strategy">
        <div className="h-96 flex items-center justify-center text-gray-500">No stint data available</div>
      </Card>
    );
  }

  // Custom bar renderer for stint segments
  const CustomBar = (props: any) => {
    const { x, y, width, height, fill, payload } = props;

    // Extract stint data from payload
    const stints = Object.entries(payload)
      .filter(([key]) => key.startsWith("stint_"))
      .map(([key, value]: [string, any]) => value)
      .sort((a, b) => a.start - b.start);

    if (stints.length === 0) return null;

    const maxLap = Math.max(...stints.map((s: any) => s.end));
    const totalWidth = width;

    return (
      <g>
        {stints.map((stint: any, index: number) => {
          // Calculate position and width based on lap range
          // Start position: stint.start is the lap number where this stint begins
          // Width: (stint.end - stint.start + 1) gives the number of laps in the stint
          const stintStart = stint.start || 0;
          const stintEnd = stint.end || stint.start || 0;
          const stintLaps = stintEnd - stintStart + 1;

          // Normalize to chart width (0-based, so stint starting at lap 1 should be at x position 0)
          const stintX = x + ((stintStart - 1) / maxLap) * totalWidth;
          const stintWidth = (stintLaps / maxLap) * totalWidth;

          return (
            <rect
              key={index}
              x={stintX}
              y={y}
              width={stintWidth}
              height={height}
              fill={COMPOUND_COLORS[stint.compound] || "#999"}
              stroke="#000"
              strokeWidth={1}
            />
          );
        })}
      </g>
    );
  };

  return (
    <Card title="Tyre Strategy">
      <div className="mb-4">
        <div className="flex gap-4 text-sm">
          {Object.entries(COMPOUND_COLORS).map(([compound, color]) => (
            <div key={compound} className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-400" style={{ backgroundColor: color }} />
              <span>{compound}</span>
            </div>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" label={{ value: "Lap Number", position: "insideBottom", offset: -5 }} />
          <YAxis dataKey="driver" type="category" width={80} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151" }}
            content={({ active, payload }) => {
              if (!active || !payload || !payload[0]) return null;

              const data = payload[0].payload;
              const stints = Object.entries(data)
                .filter(([key]) => key.startsWith("stint_"))
                .map(([key, value]: [string, any]) => value);

              return (
                <div className="bg-gray-800 border border-gray-600 p-3 rounded">
                  <div className="font-bold mb-2">{data.driver}</div>
                  {stints.map((stint: any, i: number) => (
                    <div key={i} className="text-sm">
                      Stint {i + 1}: {stint.compound} ({stint.laps} laps)
                    </div>
                  ))}
                </div>
              );
            }}
          />
          <Bar dataKey="driver" shape={<CustomBar />} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
