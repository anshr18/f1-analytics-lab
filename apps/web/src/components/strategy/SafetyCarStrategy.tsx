"use client";

import { useState } from "react";
import {
  Zap,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Users,
  Award,
  Clock,
  Info,
} from "lucide-react";
import { analyzeSafetyCar } from "@/lib/api/strategy";
import type {
  SafetyCarResponse,
  DriverStateInput,
} from "@/types/strategy";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";
import { motion } from "framer-motion";

interface SafetyCarStrategyProps {
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

const COMPOUND_OPTIONS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"];

export default function SafetyCarStrategy({ sessionId }: SafetyCarStrategyProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<SafetyCarResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [safetyCarLap, setSafetyCarLap] = useState(35);
  const [totalLaps, setTotalLaps] = useState(57);
  const [trackStatus, setTrackStatus] = useState("SC");
  const [numDrivers, setNumDrivers] = useState(8);

  // Driver states - default to 8 drivers
  const [driverStates, setDriverStates] = useState<DriverStateInput[]>(
    Array.from({ length: 8 }, (_, i) => ({
      driver_id: DRIVER_OPTIONS[i],
      position: i + 1,
      tyre_age: 10 + Math.floor(Math.random() * 15),
      compound: i % 3 === 0 ? "SOFT" : i % 3 === 1 ? "MEDIUM" : "HARD",
      gap_to_leader: i * 3.5,
      gap_to_next: i === 0 ? 0 : 3.5,
    }))
  );

  const handleNumDriversChange = (newNum: number) => {
    setNumDrivers(newNum);
    if (newNum > driverStates.length) {
      // Add more drivers
      const newDrivers = Array.from(
        { length: newNum - driverStates.length },
        (_, i) => ({
          driver_id: DRIVER_OPTIONS[driverStates.length + i] || `DR${driverStates.length + i + 1}`,
          position: driverStates.length + i + 1,
          tyre_age: 15,
          compound: "MEDIUM" as const,
          gap_to_leader: (driverStates.length + i) * 3.5,
          gap_to_next: 3.5,
        })
      );
      setDriverStates([...driverStates, ...newDrivers]);
    } else {
      // Remove drivers
      setDriverStates(driverStates.slice(0, newNum));
    }
  };

  const updateDriver = (index: number, field: keyof DriverStateInput, value: any) => {
    const newStates = [...driverStates];
    newStates[index] = { ...newStates[index], [field]: value };
    setDriverStates(newStates);
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);

    try {
      const response = await analyzeSafetyCar({
        session_id: sessionId,
        safety_car_lap: safetyCarLap,
        total_laps: totalLaps,
        driver_states: driverStates,
        track_status: trackStatus,
      });

      setResult(response);
    } catch (err: any) {
      console.error("Safety car analysis failed:", err);
      setError(err.message || "Failed to analyze safety car scenario. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case "PIT":
        return CheckCircle2;
      case "STAY_OUT":
        return XCircle;
      default:
        return AlertTriangle;
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "PIT":
        return "text-green-400";
      case "STAY_OUT":
        return "text-blue-400";
      default:
        return "text-yellow-400";
    }
  };

  const getRecommendationBg = (recommendation: string) => {
    switch (recommendation) {
      case "PIT":
        return "bg-green-900/20 border-green-700/30";
      case "STAY_OUT":
        return "bg-blue-900/20 border-blue-700/30";
      default:
        return "bg-yellow-900/20 border-yellow-700/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-5 h-5 text-[var(--color-primary)]" />
          <div>
            <h3 className="text-lg font-semibold">Safety Car Scenario</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Configure field state during safety car period
            </p>
          </div>
        </div>

        {/* Race Configuration */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              Safety Car Lap
            </label>
            <input
              type="number"
              value={safetyCarLap}
              onChange={(e) => setSafetyCarLap(Number(e.target.value))}
              min="1"
              max={totalLaps}
              className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
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

        {/* Driver Configuration Table */}
        <div className="mb-6">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-[var(--color-info)]" />
            Field Configuration
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)]">
                  <th className="text-left py-2 px-2">Pos</th>
                  <th className="text-left py-2 px-2">Driver</th>
                  <th className="text-left py-2 px-2">Tyre Age</th>
                  <th className="text-left py-2 px-2">Compound</th>
                  <th className="text-left py-2 px-2">Gap to Leader</th>
                  <th className="text-left py-2 px-2">Gap to Next</th>
                </tr>
              </thead>
              <tbody>
                {driverStates.map((driver, idx) => (
                  <tr key={idx} className="border-b border-[var(--color-border)]">
                    <td className="py-2 px-2">
                      <span className="font-mono font-bold">P{driver.position}</span>
                    </td>
                    <td className="py-2 px-2">
                      <select
                        value={driver.driver_id}
                        onChange={(e) => updateDriver(idx, "driver_id", e.target.value)}
                        className="w-20 px-2 py-1 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-xs"
                      >
                        {DRIVER_OPTIONS.map((d) => (
                          <option key={d} value={d}>
                            {d}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="py-2 px-2">
                      <input
                        type="number"
                        value={driver.tyre_age}
                        onChange={(e) => updateDriver(idx, "tyre_age", Number(e.target.value))}
                        min="0"
                        max="50"
                        className="w-16 px-2 py-1 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-xs"
                      />
                    </td>
                    <td className="py-2 px-2">
                      <select
                        value={driver.compound}
                        onChange={(e) => updateDriver(idx, "compound", e.target.value)}
                        className="w-24 px-2 py-1 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-xs"
                      >
                        {COMPOUND_OPTIONS.map((c) => (
                          <option key={c} value={c}>
                            {c}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="py-2 px-2">
                      <input
                        type="number"
                        value={driver.gap_to_leader}
                        onChange={(e) => updateDriver(idx, "gap_to_leader", Number(e.target.value))}
                        step="0.1"
                        min="0"
                        className="w-20 px-2 py-1 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-xs"
                      />
                    </td>
                    <td className="py-2 px-2">
                      <input
                        type="number"
                        value={driver.gap_to_next}
                        onChange={(e) => updateDriver(idx, "gap_to_next", Number(e.target.value))}
                        step="0.1"
                        min="0"
                        className="w-20 px-2 py-1 bg-[var(--color-background)] border border-[var(--color-border)] rounded text-xs"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-900/20 border border-red-700/30 rounded-lg text-red-400 text-sm mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={analyzing || !sessionId}
          className="w-full py-3.5 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-orange-500/20"
        >
          <Shield className="w-4 h-4" />
          {analyzing ? "Analyzing..." : "Analyze Safety Car Scenario"}
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
          {/* Field Summary */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
            <div className="flex items-center gap-3 mb-6">
              <Award className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Field Summary</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Total Drivers
                </div>
                <div className="text-2xl font-bold">{result.field_summary.total_drivers}</div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Avg Tyre Age
                </div>
                <div className="text-2xl font-bold">
                  {result.field_summary.avg_tyre_age.toFixed(1)} laps
                </div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Laps Remaining
                </div>
                <div className="text-2xl font-bold">{result.laps_remaining}</div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Drivers on Old Tyres
                </div>
                <div className="text-2xl font-bold text-orange-400">
                  {result.field_summary.drivers_on_old_tyres}
                </div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  Drivers on Fresh Tyres
                </div>
                <div className="text-2xl font-bold text-green-400">
                  {result.field_summary.drivers_on_fresh_tyres}
                </div>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg p-4">
                <div className="text-sm text-[var(--color-text-secondary)] mb-1">
                  SC Pit Advantage
                </div>
                <div className="text-2xl font-bold text-purple-400">
                  {result.field_summary.pit_window_advantage ? "Yes" : "No"}
                </div>
              </div>
            </div>

            {/* Strategic Overview */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-4">
                <div className="text-sm font-semibold text-green-400 mb-2">
                  Should PIT ({result.drivers_who_should_pit.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.drivers_who_should_pit.map((driver) => (
                    <span
                      key={driver}
                      className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs font-mono"
                    >
                      {driver}
                    </span>
                  ))}
                  {result.drivers_who_should_pit.length === 0 && (
                    <span className="text-sm text-[var(--color-text-secondary)]">None</span>
                  )}
                </div>
              </div>
              <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4">
                <div className="text-sm font-semibold text-blue-400 mb-2">
                  Should STAY OUT ({result.drivers_who_should_stay.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.drivers_who_should_stay.map((driver) => (
                    <span
                      key={driver}
                      className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-mono"
                    >
                      {driver}
                    </span>
                  ))}
                  {result.drivers_who_should_stay.length === 0 && (
                    <span className="text-sm text-[var(--color-text-secondary)]">None</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Driver Decisions */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />
              <h3 className="text-lg font-semibold">Driver-by-Driver Recommendations</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.decisions.map((decision) => {
                const Icon = getRecommendationIcon(decision.recommendation);
                const color = getRecommendationColor(decision.recommendation);
                const bgClass = getRecommendationBg(decision.recommendation);

                return (
                  <div
                    key={decision.driver_id}
                    className={`border rounded-lg p-4 ${bgClass}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-mono font-bold">
                          P{decision.current_position}
                        </span>
                        <span className="text-lg font-bold">{decision.driver_id}</span>
                      </div>
                      <Icon className={`w-6 h-6 ${color}`} />
                    </div>

                    <div className={`text-sm font-bold mb-2 ${color}`}>
                      {decision.recommendation.replace("_", " ")}
                    </div>

                    <div className="text-xs text-[var(--color-text-secondary)] mb-3">
                      {decision.reasoning}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div>
                        <div className="text-[var(--color-text-secondary)]">If PIT</div>
                        <div className="font-bold">
                          P{decision.predicted_position_if_pit}
                          {decision.position_gain_if_pit > 0 && (
                            <span className="text-green-400 ml-1">
                              ↑{decision.position_gain_if_pit}
                            </span>
                          )}
                          {decision.position_loss_if_pit > 0 && (
                            <span className="text-red-400 ml-1">
                              ↓{decision.position_loss_if_pit}
                            </span>
                          )}
                        </div>
                      </div>
                      <div>
                        <div className="text-[var(--color-text-secondary)]">If STAY</div>
                        <div className="font-bold">P{decision.predicted_position_if_stay}</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[var(--color-text-secondary)]">Confidence</span>
                      <span className="font-bold">{(decision.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="mt-1 bg-[var(--color-background)] rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          decision.confidence > 0.7
                            ? "bg-green-400"
                            : decision.confidence > 0.4
                            ? "bg-yellow-400"
                            : "bg-red-400"
                        }`}
                        style={{ width: `${decision.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendation Distribution Chart */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6"
          >
            <div className="text-sm font-semibold mb-4">Recommendation Distribution</div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    {
                      name: "PIT",
                      value: result.drivers_who_should_pit.length,
                      fill: "#10b981",
                    },
                    {
                      name: "STAY OUT",
                      value: result.drivers_who_should_stay.length,
                      fill: "#3b82f6",
                    },
                    {
                      name: "RISKY",
                      value:
                        result.decisions.length -
                        result.drivers_who_should_pit.length -
                        result.drivers_who_should_stay.length,
                      fill: "#f59e0b",
                    },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  dataKey="value"
                >
                  {[0, 1, 2].map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        index === 0
                          ? "#10b981"
                          : index === 1
                          ? "#3b82f6"
                          : "#f59e0b"
                      }
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#141414",
                    border: "1px solid #262626",
                    borderRadius: "8px",
                    color: "#fafafa",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </motion.div>
      )}

      {!result && (
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-12 text-center">
          <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-[var(--color-primary)]" />
          </div>
          <h3 className="text-lg font-semibold mb-2">
            No analysis yet
          </h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Configure the field state and click &quot;Analyze Safety Car Scenario&quot;
          </p>
        </div>
      )}
    </div>
  );
}
