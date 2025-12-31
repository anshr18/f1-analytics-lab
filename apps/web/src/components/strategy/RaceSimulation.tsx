"use client";

import React, { useState, useEffect } from "react";
import {
  Flag,
  Play,
  Pause,
  RotateCcw,
  Trophy,
  Clock,
  TrendingUp,
  Users,
  Award,
} from "lucide-react";
import { simulateRace } from "@/lib/api/strategy";
import type { RaceSimulationResponse } from "@/types/strategy";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";

interface RaceSimulationProps {
  sessionId: string;
}

const DRIVER_OPTIONS = [
  "VER",
  "LEC",
  "HAM",
  "NOR",
  "SAI",
  "PER",
  "RUS",
  "ALO",
  "PIA",
  "STR",
  "GAS",
  "TSU",
  "ALB",
  "SAR",
  "HUL",
  "MAG",
  "RIC",
  "BOT",
  "ZHO",
  "OCO",
];

const DRIVER_COLORS: { [key: string]: string } = {
  VER: "#3671C6",
  LEC: "#E8002D",
  HAM: "#27F4D2",
  NOR: "#FF8000",
  SAI: "#E8002D",
  PER: "#3671C6",
  RUS: "#27F4D2",
  ALO: "#229971",
  PIA: "#FF8000",
  STR: "#229971",
  GAS: "#5E8FAA",
  TSU: "#5E8FAA",
  ALB: "#64C4FF",
  SAR: "#64C4FF",
  HUL: "#B6BABD",
  MAG: "#B6BABD",
  RIC: "#6692FF",
  BOT: "#52E252",
  ZHO: "#52E252",
  OCO: "#FF87BC",
};

export default function RaceSimulation({ sessionId }: RaceSimulationProps) {
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<RaceSimulationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Animation state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentLap, setCurrentLap] = useState(0);

  // Form state
  const [totalLaps, setTotalLaps] = useState(57);
  const [numDrivers, setNumDrivers] = useState(8);
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>(
    DRIVER_OPTIONS.slice(0, 8)
  );
  const [pitStrategies, setPitStrategies] = useState<{ [key: string]: string }>(
    Object.fromEntries(DRIVER_OPTIONS.slice(0, 8).map((d) => [d, "20,40"]))
  );

  const handleNumDriversChange = (newNum: number) => {
    setNumDrivers(newNum);
    const newDrivers = DRIVER_OPTIONS.slice(0, newNum);
    setSelectedDrivers(newDrivers);

    // Initialize pit strategies for new drivers
    const newStrats: { [key: string]: string } = {};
    newDrivers.forEach((driver) => {
      newStrats[driver] = pitStrategies[driver] || "20,40";
    });
    setPitStrategies(newStrats);
  };

  const updatePitStrategy = (driver: string, value: string) => {
    setPitStrategies({ ...pitStrategies, [driver]: value });
  };

  const handleSimulate = async () => {
    setSimulating(true);
    setError(null);
    setCurrentLap(0);
    setIsPlaying(false);

    try {
      // Parse pit strategies
      const parsedStrategies: { [key: string]: number[] } = {};
      for (const [driver, laps] of Object.entries(pitStrategies)) {
        const lapNumbers = laps
          .split(",")
          .map((l) => parseInt(l.trim()))
          .filter((l) => !isNaN(l) && l > 0 && l <= totalLaps);
        parsedStrategies[driver] = lapNumbers;
      }

      const response = await simulateRace({
        session_id: sessionId,
        total_laps: totalLaps,
        drivers: selectedDrivers,
        pit_strategies: parsedStrategies,
      });

      setResult(response);
    } catch (err: any) {
      console.error("Race simulation failed:", err);
      setError(err.message || "Failed to simulate race. Please try again.");
    } finally {
      setSimulating(false);
    }
  };

  const togglePlayPause = () => {
    if (!result) return;

    if (isPlaying) {
      setIsPlaying(false);
    } else {
      if (currentLap >= result.lap_by_lap_positions.length - 1) {
        setCurrentLap(0);
      }
      setIsPlaying(true);
    }
  };

  const resetAnimation = () => {
    setCurrentLap(0);
    setIsPlaying(false);
  };

  // Auto-advance animation
  useEffect(() => {
    if (isPlaying && result) {
      const interval = setInterval(() => {
        setCurrentLap((prev) => {
          if (prev >= result.lap_by_lap_positions.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 500); // 500ms per lap

      return () => clearInterval(interval);
    }
  }, [isPlaying, result]);

  const getCurrentPositions = () => {
    if (!result || currentLap >= result.lap_by_lap_positions.length) {
      return [];
    }
    const lapData = result.lap_by_lap_positions[currentLap];
    return Object.entries(lapData)
      .map(([driver, position]) => ({ driver, position }))
      .sort((a, b) => a.position - b.position);
  };

  const getPositionHistory = () => {
    if (!result) return [];

    const drivers = selectedDrivers;
    const laps = result.lap_by_lap_positions;

    return laps.map((lapData, lapIndex) => {
      const lapEntry: any = { lap: lapIndex + 1 };
      drivers.forEach((driver) => {
        lapEntry[driver] = lapData[driver];
      });
      return lapEntry;
    });
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
        <div className="flex items-center gap-3 mb-6">
          <Flag className="w-5 h-5 text-[var(--color-primary)]" />
          <div>
            <h3 className="text-lg font-semibold">Race Simulation Setup</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Configure full race with pit strategies
            </p>
          </div>
        </div>

        {/* Race Configuration */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              Total Laps
            </label>
            <input
              type="number"
              value={totalLaps}
              onChange={(e) => setTotalLaps(Number(e.target.value))}
              min="1"
              max="78"
              className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              Number of Drivers
            </label>
            <select
              value={numDrivers}
              onChange={(e) => handleNumDriversChange(Number(e.target.value))}
              className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              {[4, 6, 8, 10, 12, 15, 20].map((num) => (
                <option key={num} value={num}>
                  {num} drivers
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Pit Strategy Configuration */}
        <div className="mb-6">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-[var(--color-info)]" />
            Pit Stop Strategies
            <span className="text-xs text-[var(--color-text-secondary)] font-normal">
              (Enter lap numbers separated by commas, e.g., "20,40")
            </span>
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {selectedDrivers.map((driver) => (
              <div key={driver}>
                <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
                  {driver}
                </label>
                <input
                  type="text"
                  value={pitStrategies[driver] || ""}
                  onChange={(e) => updatePitStrategy(driver, e.target.value)}
                  placeholder="e.g., 20,40"
                  className="w-full px-3 py-2 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-sm font-mono"
                />
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-900/20 border border-red-700/30 rounded-lg text-red-400 text-sm mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleSimulate}
          disabled={simulating || !sessionId}
          className="w-full py-3.5 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-red-500/20"
        >
          <Flag className="w-4 h-4" />
          {simulating ? "Simulating Race..." : "Simulate Full Race"}
        </button>
      </div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          {/* Race Summary */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
            <div className="flex items-center gap-3 mb-6">
              <Trophy className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Race Results</h3>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Race Winner
                </div>
                <div className="text-2xl font-bold text-yellow-400">
                  {Object.entries(result.final_classification).find(
                    ([, pos]) => pos === 1
                  )?.[0] || "N/A"}
                </div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Total Laps
                </div>
                <div className="text-2xl font-bold">
                  {result.lap_by_lap_positions.length}
                </div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Fastest Lap
                </div>
                <div className="text-lg font-bold text-purple-400">
                  {result.fastest_lap?.driver || "N/A"} - Lap{" "}
                  {result.fastest_lap?.lap || "N/A"}
                </div>
              </div>
            </div>

            {/* Final Classification */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Award className="w-4 h-4 text-[var(--color-warning)]" />
                Final Classification
              </h4>
              <div className="space-y-2">
                {Object.entries(result.final_classification)
                  .sort(([, posA], [, posB]) => posA - posB)
                  .map(([driver, position], idx) => (
                    <motion.div
                      key={driver}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: idx * 0.05 }}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        position === 1
                          ? "bg-yellow-900/20 border border-yellow-700/30"
                          : position === 2
                          ? "bg-gray-600/20 border border-gray-500/30"
                          : position === 3
                          ? "bg-orange-900/20 border border-orange-700/30"
                          : "bg-[var(--color-background)]"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {position === 1 && (
                          <Trophy className="w-5 h-5 text-yellow-400" />
                        )}
                        <span className="font-mono text-lg font-bold">
                          P{position}
                        </span>
                        <span className="font-medium">{driver}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-xs text-[var(--color-text-secondary)]">
                          {result.total_pit_stops[driver]} stop
                          {result.total_pit_stops[driver] !== 1 ? "s" : ""}
                        </div>
                      </div>
                    </motion.div>
                  ))}
              </div>
            </div>
          </div>

          {/* Lap-by-Lap Playback */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Play className="w-5 h-5 text-[var(--color-primary)]" />
                <h3 className="text-lg font-semibold">Lap-by-Lap Playback</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={resetAnimation}
                  className="px-3 py-2 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-border)] transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
                <button
                  onClick={togglePlayPause}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-4 h-4" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Play
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Lap Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-[var(--color-text-secondary)]">
                  Lap Progress
                </span>
                <span className="text-lg font-bold">
                  Lap {currentLap + 1} / {result.lap_by_lap_positions.length}
                </span>
              </div>
              <div className="bg-[var(--color-background)] rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-[var(--color-primary)] transition-all duration-300"
                  style={{
                    width: `${
                      ((currentLap + 1) / result.lap_by_lap_positions.length) *
                      100
                    }%`,
                  }}
                />
              </div>
              <input
                type="range"
                min="0"
                max={result.lap_by_lap_positions.length - 1}
                value={currentLap}
                onChange={(e) => {
                  setCurrentLap(Number(e.target.value));
                  setIsPlaying(false);
                }}
                className="w-full mt-2"
              />
            </div>

            {/* Current Standings */}
            <div className="bg-[var(--color-background)] rounded-lg p-4">
              <h4 className="font-semibold mb-3 text-sm">
                Current Standings (Lap {currentLap + 1})
              </h4>
              <div className="space-y-2">
                <AnimatePresence mode="popLayout">
                  {getCurrentPositions().map(({ driver, position }) => (
                    <motion.div
                      key={driver}
                      layout
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="flex items-center justify-between p-2 rounded bg-[var(--color-surface)] border border-[var(--color-border)]"
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-mono font-bold w-8">
                          P{position}
                        </span>
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{
                            backgroundColor:
                              DRIVER_COLORS[driver] || "#999999",
                          }}
                        />
                        <span className="font-medium">{driver}</span>
                      </div>
                      {pitStrategies[driver]
                        ?.split(",")
                        .map((l) => parseInt(l.trim()))
                        .includes(currentLap + 1) && (
                        <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded">
                          PIT STOP
                        </span>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>

          {/* Position History Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Position History</h3>
            </div>

            <div className="bg-[var(--color-background)] rounded-lg p-4">
              <ResponsiveContainer width="100%" height={400}>
                <LineChart
                  data={getPositionHistory()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis
                    dataKey="lap"
                    stroke="#a3a3a3"
                    label={{
                      value: "Lap",
                      position: "insideBottom",
                      offset: -5,
                      fill: "#a3a3a3",
                    }}
                  />
                  <YAxis
                    reversed
                    stroke="#a3a3a3"
                    domain={[1, numDrivers]}
                    ticks={Array.from(
                      { length: numDrivers },
                      (_, i) => i + 1
                    )}
                    label={{
                      value: "Position",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#a3a3a3",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#141414",
                      border: "1px solid #262626",
                      borderRadius: "8px",
                      color: "#fafafa",
                    }}
                    formatter={(value: any, name: string) => [
                      `P${value}`,
                      name,
                    ]}
                  />
                  <Legend />
                  {selectedDrivers.map((driver) => (
                    <Line
                      key={driver}
                      type="monotone"
                      dataKey={driver}
                      stroke={DRIVER_COLORS[driver] || "#999999"}
                      strokeWidth={2}
                      dot={{ r: 2 }}
                      name={driver}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Pit Stop Analysis */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <Clock className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Pit Stop Analysis</h3>
            </div>

            <div className="bg-[var(--color-background)] rounded-lg p-4">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={Object.entries(result.total_pit_stops).map(
                    ([driver, stops]) => ({
                      driver,
                      stops,
                      fill: DRIVER_COLORS[driver] || "#999999",
                    })
                  )}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="driver" stroke="#a3a3a3" />
                  <YAxis
                    stroke="#a3a3a3"
                    label={{
                      value: "Pit Stops",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#a3a3a3",
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#141414",
                      border: "1px solid #262626",
                      borderRadius: "8px",
                      color: "#fafafa",
                    }}
                  />
                  <Bar dataKey="stops" radius={[8, 8, 0, 0]}>
                    {Object.entries(result.total_pit_stops).map(
                      ([driver], index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={DRIVER_COLORS[driver] || "#999999"}
                        />
                      )
                    )}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Race Summary */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Flag className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Race Summary</h3>
            </div>
            <p className="text-sm text-[var(--color-text-secondary)]">
              {result.summary}
            </p>
          </div>
        </motion.div>
      )}

      {!result && (
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-12 text-center">
          <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Flag className="w-8 h-8 text-[var(--color-primary)]" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No simulation yet</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Configure pit strategies and click &quot;Simulate Full Race&quot;
          </p>
        </div>
      )}
    </div>
  );
}
