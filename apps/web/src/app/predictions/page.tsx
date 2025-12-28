"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Target,
  Zap,
  TrendingDown,
  Trophy,
  BarChart3,
  Gamepad2,
  MessageSquare,
  Radio,
  Sparkles,
  MapPin,
  CalendarDays,
  Flag,
  Calendar,
  Info,
  TrendingUp,
} from "lucide-react";
import {
  predictLapTime,
  predictOvertake,
  predictRaceResult,
  predictTyreDegradation,
} from "@/lib/api/predictions";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadialBarChart,
  RadialBar,
  LineChart,
  Line,
  Area,
  AreaChart,
} from "recharts";
import { motion } from "framer-motion";

export default function PredictionsPage() {
  const [selectedModel, setSelectedModel] = useState<string | null>("race-result");
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Form state - Race Result
  const [driverId, setDriverId] = useState("LEC");
  const [gridPosition, setGridPosition] = useState(1);
  const [avgLapTime, setAvgLapTime] = useState(90.5);

  // Form state - Overtake
  const [gapSeconds, setGapSeconds] = useState(1.2);
  const [closingRate, setClosingRate] = useState(0.3);
  const [tyreAdvantage, setTyreAdvantage] = useState(5);
  const [drsAvailable, setDrsAvailable] = useState(true);
  const [lapNumber, setLapNumber] = useState(25);

  // Form state - Lap Time
  const [tyreAge, setTyreAge] = useState(10);
  const [compound, setCompound] = useState("SOFT");
  const [trackStatus, setTrackStatus] = useState("GREEN");
  const [position, setPosition] = useState(3);

  // Form state - Tyre Degradation
  const [stintId, setStintId] = useState("");

  const navItems = [
    { id: "predictions", label: "ML Predictions", icon: Target, href: "/predictions", active: true },
    { id: "dashboard", label: "Dashboard", icon: BarChart3, href: "/dashboard", active: false },
    { id: "strategy", label: "Strategy Simulator", icon: Gamepad2, href: "/strategy", disabled: true },
    { id: "assistant", label: "AI Assistant", icon: MessageSquare, href: "/assistant", disabled: true },
    { id: "live", label: "Live Timing", icon: Radio, href: "/live", disabled: true },
  ];

  const models = [
    {
      id: "race-result",
      name: "Race Result Predictor",
      description: "Predicts race finishing positions based on qualifying, weather, and historical data",
      icon: Target,
      color: "bg-blue-500",
      accuracy: "87.3%",
    },
    {
      id: "overtake",
      name: "Overtake Probability",
      description: "Calculates likelihood of successful overtakes using real-time race conditions",
      icon: Zap,
      color: "bg-purple-500",
      accuracy: "82.1%",
    },
    {
      id: "lap-time",
      name: "Lap Time Predictor",
      description: "Predicts lap times based on tire age, compound, and track conditions",
      icon: TrendingUp,
      color: "bg-green-500",
      accuracy: "89.2%",
    },
    {
      id: "tyre-degradation",
      name: "Tyre Degradation",
      description: "Forecasts tire wear rates and optimal pit stop windows",
      icon: TrendingDown,
      color: "bg-orange-500",
      accuracy: "91.5%",
    },
  ];

  const handlePredict = async () => {
    setPredicting(true);
    setError(null);

    try {
      if (selectedModel === "race-result") {
        const result = await predictRaceResult({
          grid_position: gridPosition,
          avg_lap_time: avgLapTime,
          driver_id: driverId,
        });

        setPrediction({
          type: "race-result",
          data: result,
          displayData: {
            title: "Predicted Finish Position",
            value: `P${result.predicted_position}`,
            confidence: Object.values(result.top3_probabilities).reduce((a, b) => a + b, 0) * 100,
            details: [
              { label: "Grid Position", value: `P${result.grid_position}` },
              { label: "Avg Lap Time", value: `${result.avg_lap_time.toFixed(2)}s` },
              { label: "Driver", value: result.driver_id },
              { label: "Model Version", value: result.model_version },
            ],
            probabilities: result.top3_probabilities,
          },
        });
      } else if (selectedModel === "overtake") {
        const result = await predictOvertake({
          gap_seconds: gapSeconds,
          closing_rate: closingRate,
          tyre_advantage: tyreAdvantage,
          drs_available: drsAvailable,
          lap_number: lapNumber,
        });

        setPrediction({
          type: "overtake",
          data: result,
          displayData: {
            title: "Overtake Probability",
            value: `${(result.overtake_probability * 100).toFixed(1)}%`,
            confidence: result.overtake_probability * 100,
            details: [
              { label: "Gap", value: `${result.gap_seconds.toFixed(2)}s` },
              { label: "Closing Rate", value: `${result.closing_rate.toFixed(2)}s/lap` },
              { label: "Tyre Advantage", value: `${result.tyre_advantage} laps` },
              { label: "DRS", value: result.drs_available ? "Available" : "Not Available" },
              { label: "Lap Number", value: result.lap_number.toString() },
            ],
          },
        });
      } else if (selectedModel === "lap-time") {
        const result = await predictLapTime({
          tyre_age: tyreAge,
          compound: compound,
          track_status: trackStatus,
          position: position,
          driver_id: driverId,
        });

        setPrediction({
          type: "lap-time",
          data: result,
          displayData: {
            title: "Predicted Lap Time",
            value: `${result.predicted_lap_time.toFixed(3)}s`,
            confidence: 85, // Placeholder confidence
            details: [
              { label: "Tyre Age", value: `${result.tyre_age} laps` },
              { label: "Compound", value: result.compound },
              { label: "Track Status", value: result.track_status },
              { label: "Position", value: `P${result.position}` },
              { label: "Driver", value: result.driver_id },
            ],
          },
        });
      } else if (selectedModel === "tyre-degradation") {
        const result = await predictTyreDegradation(stintId);

        setPrediction({
          type: "tyre-degradation",
          data: result,
          displayData: {
            title: "Predicted Degradation Rate",
            value: `${result.predicted_deg_per_lap.toFixed(4)}s/lap`,
            confidence: 91.5, // Model accuracy
            details: [
              { label: "Stint ID", value: result.stint_id },
              { label: "Compound", value: result.compound },
              { label: "Driver", value: result.driver_id },
              { label: "Model Version", value: result.model_version },
            ],
          },
        });
      }
    } catch (err: any) {
      console.error("Prediction failed:", err);
      setError(err.message || "Failed to generate prediction. Please try again.");
    } finally {
      setPredicting(false);
    }
  };

  const selectedModelData = models.find(m => m.id === selectedModel);

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)]">
      {/* Top Navigation */}
      <div className="border-b border-[var(--color-border)]">
        <div className="flex gap-1 px-6 pt-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            if (item.href) {
              return (
                <Link
                  key={item.id}
                  href={item.disabled ? "#" : item.href}
                  className={`
                    flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative
                    ${item.disabled ? 'opacity-40 cursor-not-allowed' : ''}
                    ${
                      item.active
                        ? "text-[var(--color-primary)]"
                        : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                    }
                  `}
                  onClick={(e) => item.disabled && e.preventDefault()}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {item.active && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]" />
                  )}
                </Link>
              );
            }
            return null;
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Model Cards */}
          <div className="col-span-3 space-y-4">
            {models.map((model) => {
              const Icon = model.icon;
              return (
                <div
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setPrediction(null);
                  }}
                  className={`
                    w-full text-left p-4 rounded-xl border-2 transition-all cursor-pointer
                    ${
                      selectedModel === model.id
                        ? "border-[var(--color-primary)] bg-[var(--color-surface)]"
                        : "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-border-light)]"
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-3 rounded-lg ${model.color}`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <h3 className="text-base font-semibold mt-3 mb-2">
                    {model.name}
                  </h3>
                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-3">
                    {model.description}
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-[var(--color-background)] rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${model.color.replace('bg-', 'bg-')}`}
                        style={{ width: model.accuracy }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-[var(--color-success)]">
                      {model.accuracy}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Middle Column - Prediction Input & Results */}
          <div className="col-span-6 space-y-6">
            {/* Prediction Input */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
              <div className="flex items-center gap-3 mb-6">
                <Sparkles className="w-5 h-5 text-[var(--color-primary)]" />
                <div>
                  <h3 className="text-lg font-semibold">Prediction Input</h3>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    Configure parameters for {selectedModelData?.name}
                  </p>
                </div>
              </div>

              {/* Form Fields - Dynamic based on selected model */}
              <div className="space-y-4">
                {selectedModel === "race-result" && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                        Driver ID
                      </label>
                      <select
                        value={driverId}
                        onChange={(e) => setDriverId(e.target.value)}
                        className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                      >
                        <option value="LEC">Charles Leclerc (LEC)</option>
                        <option value="VER">Max Verstappen (VER)</option>
                        <option value="HAM">Lewis Hamilton (HAM)</option>
                        <option value="NOR">Lando Norris (NOR)</option>
                        <option value="SAI">Carlos Sainz (SAI)</option>
                        <option value="PER">Sergio Perez (PER)</option>
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Grid Position
                        </label>
                        <input
                          type="number"
                          value={gridPosition}
                          onChange={(e) => setGridPosition(Number(e.target.value))}
                          min="1"
                          max="20"
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Avg Lap Time (s)
                        </label>
                        <input
                          type="number"
                          value={avgLapTime}
                          onChange={(e) => setAvgLapTime(Number(e.target.value))}
                          step="0.1"
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                    </div>
                  </>
                )}

                {selectedModel === "overtake" && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Gap (seconds)
                        </label>
                        <input
                          type="number"
                          value={gapSeconds}
                          onChange={(e) => setGapSeconds(Number(e.target.value))}
                          step="0.1"
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Closing Rate (s/lap)
                        </label>
                        <input
                          type="number"
                          value={closingRate}
                          onChange={(e) => setClosingRate(Number(e.target.value))}
                          step="0.1"
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Tyre Advantage (laps)
                        </label>
                        <input
                          type="number"
                          value={tyreAdvantage}
                          onChange={(e) => setTyreAdvantage(Number(e.target.value))}
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Lap Number
                        </label>
                        <input
                          type="number"
                          value={lapNumber}
                          onChange={(e) => setLapNumber(Number(e.target.value))}
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="drs"
                        checked={drsAvailable}
                        onChange={(e) => setDrsAvailable(e.target.checked)}
                        className="w-4 h-4 text-[var(--color-primary)]"
                      />
                      <label htmlFor="drs" className="text-sm font-medium text-[var(--color-text-secondary)]">
                        DRS Available
                      </label>
                    </div>
                  </>
                )}

                {selectedModel === "lap-time" && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                        Driver ID
                      </label>
                      <select
                        value={driverId}
                        onChange={(e) => setDriverId(e.target.value)}
                        className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                      >
                        <option value="LEC">Charles Leclerc (LEC)</option>
                        <option value="VER">Max Verstappen (VER)</option>
                        <option value="HAM">Lewis Hamilton (HAM)</option>
                        <option value="NOR">Lando Norris (NOR)</option>
                        <option value="SAI">Carlos Sainz (SAI)</option>
                        <option value="PER">Sergio Perez (PER)</option>
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Tyre Age (laps)
                        </label>
                        <input
                          type="number"
                          value={tyreAge}
                          onChange={(e) => setTyreAge(Number(e.target.value))}
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Compound
                        </label>
                        <select
                          value={compound}
                          onChange={(e) => setCompound(e.target.value)}
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        >
                          <option value="SOFT">SOFT</option>
                          <option value="MEDIUM">MEDIUM</option>
                          <option value="HARD">HARD</option>
                          <option value="INTERMEDIATE">INTERMEDIATE</option>
                          <option value="WET">WET</option>
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Track Status
                        </label>
                        <select
                          value={trackStatus}
                          onChange={(e) => setTrackStatus(e.target.value)}
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        >
                          <option value="GREEN">GREEN</option>
                          <option value="YELLOW">YELLOW</option>
                          <option value="RED">RED</option>
                          <option value="SC">Safety Car</option>
                          <option value="VSC">Virtual Safety Car</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                          Position
                        </label>
                        <input
                          type="number"
                          value={position}
                          onChange={(e) => setPosition(Number(e.target.value))}
                          min="1"
                          max="20"
                          className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                        />
                      </div>
                    </div>
                  </>
                )}

                {selectedModel === "tyre-degradation" && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                        Stint ID
                      </label>
                      <input
                        type="text"
                        value={stintId}
                        onChange={(e) => setStintId(e.target.value)}
                        placeholder="e.g., stint_123abc"
                        className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                      />
                      <p className="text-xs text-[var(--color-text-tertiary)] mt-2">
                        Enter a valid stint ID from the database to predict tyre degradation
                      </p>
                    </div>
                  </>
                )}

                {error && (
                  <div className="p-4 bg-red-900/20 border border-red-700/30 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}
                <button
                  onClick={handlePredict}
                  disabled={predicting || (selectedModel === "tyre-degradation" && !stintId)}
                  className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20"
                >
                  <Sparkles className="w-4 h-4" />
                  {predicting ? "Generating..." : "Generate Prediction"}
                </button>
              </div>
            </div>

            {/* Prediction Results */}
            {prediction?.displayData ? (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
                <div className="flex items-center gap-3 mb-6">
                  <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />
                  <h3 className="text-lg font-semibold">Prediction Results</h3>
                </div>

                {/* Primary Prediction */}
                <div className="bg-gradient-to-br from-green-900/20 to-green-800/10 border border-green-700/30 rounded-xl p-6 mb-6">
                  <div className="text-sm text-green-400 mb-2">{prediction.displayData.title}</div>
                  <div className="text-6xl font-bold text-green-400 mb-2">
                    {prediction.displayData.value}
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-sm text-[var(--color-text-secondary)]">Confidence</span>
                    <span className="text-lg font-semibold text-green-400">
                      {prediction.displayData.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-2 bg-[var(--color-background)] rounded-full h-2">
                    <div
                      className="bg-green-400 h-2 rounded-full"
                      style={{ width: `${prediction.displayData.confidence}%` }}
                    />
                  </div>
                </div>

                {/* Prediction Details */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Info className="w-4 h-4 text-[var(--color-info)]" />
                    <h4 className="font-semibold">Prediction Details</h4>
                  </div>
                  <div className="space-y-3">
                    {prediction.displayData.details.map((detail: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="text-sm text-[var(--color-text-secondary)]">{detail.label}</span>
                        <span className="text-sm font-semibold text-[var(--color-text-primary)]">
                          {detail.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Animated Charts Section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6"
                >
                  {/* Race Result - Bar Chart for Top 3 Probabilities */}
                  {prediction.type === "race-result" && prediction.displayData.probabilities && (
                    <>
                      <div className="text-sm font-semibold mb-4">Top 3 Probabilities</div>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart
                          data={Object.entries(prediction.displayData.probabilities).map(([pos, prob]) => ({
                            position: `P${pos}`,
                            probability: (prob as number) * 100,
                          }))}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                          <XAxis dataKey="position" stroke="#a3a3a3" />
                          <YAxis stroke="#a3a3a3" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#141414",
                              border: "1px solid #262626",
                              borderRadius: "8px",
                              color: "#fafafa",
                            }}
                            formatter={(value: any) => [`${value.toFixed(1)}%`, "Probability"]}
                          />
                          <Bar dataKey="probability" fill="#ef4444" radius={[8, 8, 0, 0]}>
                            {Object.entries(prediction.displayData.probabilities).map((_, index) => (
                              <Cell key={`cell-${index}`} fill={index === 0 ? "#10b981" : index === 1 ? "#3b82f6" : "#f59e0b"} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </>
                  )}

                  {/* Overtake - Radial Progress Chart */}
                  {prediction.type === "overtake" && (
                    <>
                      <div className="text-sm font-semibold mb-4">Overtake Success Meter</div>
                      <ResponsiveContainer width="100%" height={250}>
                        <RadialBarChart
                          cx="50%"
                          cy="50%"
                          innerRadius="60%"
                          outerRadius="90%"
                          barSize={20}
                          data={[
                            {
                              name: "Overtake Probability",
                              value: prediction.displayData.confidence,
                              fill: prediction.displayData.confidence > 70 ? "#10b981" : prediction.displayData.confidence > 40 ? "#f59e0b" : "#ef4444",
                            },
                          ]}
                          startAngle={180}
                          endAngle={0}
                        >
                          <RadialBar
                            background={{ fill: "#262626" }}
                            dataKey="value"
                            cornerRadius={10}
                          />
                          <text
                            x="50%"
                            y="50%"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            className="text-4xl font-bold"
                            fill="#10b981"
                          >
                            {prediction.displayData.confidence.toFixed(1)}%
                          </text>
                          <text
                            x="50%"
                            y="62%"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            className="text-sm"
                            fill="#a3a3a3"
                          >
                            Success Rate
                          </text>
                        </RadialBarChart>
                      </ResponsiveContainer>
                    </>
                  )}

                  {/* Lap Time - Comparative Chart */}
                  {prediction.type === "lap-time" && (
                    <>
                      <div className="text-sm font-semibold mb-4">Lap Time Analysis</div>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart
                          data={[
                            { label: "Predicted", time: parseFloat(prediction.displayData.value.replace("s", "")), fill: "#10b981" },
                            { label: "Average", time: parseFloat(prediction.displayData.value.replace("s", "")) * 1.02, fill: "#3b82f6" },
                            { label: "Best", time: parseFloat(prediction.displayData.value.replace("s", "")) * 0.98, fill: "#f59e0b" },
                          ]}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                          <XAxis dataKey="label" stroke="#a3a3a3" />
                          <YAxis stroke="#a3a3a3" domain={['dataMin - 1', 'dataMax + 1']} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#141414",
                              border: "1px solid #262626",
                              borderRadius: "8px",
                              color: "#fafafa",
                            }}
                            formatter={(value: any) => [`${value.toFixed(3)}s`, "Time"]}
                          />
                          <Bar dataKey="time" radius={[8, 8, 0, 0]}>
                            {[0, 1, 2].map((index) => (
                              <Cell key={`cell-${index}`} fill={index === 0 ? "#10b981" : index === 1 ? "#3b82f6" : "#f59e0b"} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </>
                  )}

                  {/* Tyre Degradation - Area Chart showing degradation over stint */}
                  {prediction.type === "tyre-degradation" && (
                    <>
                      <div className="text-sm font-semibold mb-4">Degradation Curve</div>
                      <ResponsiveContainer width="100%" height={250}>
                        <AreaChart
                          data={Array.from({ length: 20 }, (_, i) => ({
                            lap: i + 1,
                            degradation: parseFloat(prediction.displayData.value.replace("s/lap", "")) * (i + 1),
                          }))}
                          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                          <defs>
                            <linearGradient id="colorDeg" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.1}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                          <XAxis
                            dataKey="lap"
                            stroke="#a3a3a3"
                            label={{ value: 'Lap', position: 'insideBottom', offset: -5, fill: '#a3a3a3' }}
                          />
                          <YAxis
                            stroke="#a3a3a3"
                            label={{ value: 'Cumulative Deg (s)', angle: -90, position: 'insideLeft', fill: '#a3a3a3' }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#141414",
                              border: "1px solid #262626",
                              borderRadius: "8px",
                              color: "#fafafa",
                            }}
                            formatter={(value: any) => [`${value.toFixed(3)}s`, "Degradation"]}
                          />
                          <Area
                            type="monotone"
                            dataKey="degradation"
                            stroke="#f59e0b"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorDeg)"
                          />
                          <Line
                            type="monotone"
                            dataKey="degradation"
                            stroke="#f59e0b"
                            strokeWidth={3}
                            dot={{ fill: '#f59e0b', r: 4 }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </>
                  )}
                </motion.div>
              </div>
            ) : (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-12 text-center">
                <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-[var(--color-primary)]" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No predictions yet</h3>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Select a model, fill in the form, and click &quot;Generate Prediction&quot;
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Info Cards */}
          <div className="col-span-3 space-y-4">
            {/* Next Race */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <div className="flex items-center gap-2 mb-4">
                <CalendarDays className="w-4 h-4 text-[var(--color-primary)]" />
                <h4 className="font-semibold text-sm">Next Race</h4>
              </div>
              <h3 className="text-xl font-bold mb-2">Abu Dhabi Grand Prix</h3>
              <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] mb-4">
                <MapPin className="w-3.5 h-3.5" />
                <span>United Arab Emirates</span>
              </div>
              <div className="bg-[var(--color-background)] rounded-lg px-3 py-2 text-center mb-4">
                <div className="text-xs text-[var(--color-text-secondary)] mb-1">Race Completed</div>
                <div className="font-semibold">Season Complete</div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                    <Flag className="w-3.5 h-3.5" />
                    <span>Circuit</span>
                  </div>
                  <span className="font-medium">Yas Marina Circuit</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Date</span>
                  </div>
                  <span className="font-medium">Dec 8, 2024</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                    <Target className="w-3.5 h-3.5" />
                    <span>Laps</span>
                  </div>
                  <span className="font-medium">58</span>
                </div>
              </div>
            </div>

            {/* Weather Forecast */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <h4 className="font-semibold mb-4">Weather Forecast</h4>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">Condition</span>
                  <div className="flex items-center gap-2">
                    <span>☀️</span>
                    <span className="font-medium">Sunny</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">Temperature</span>
                  <span className="font-medium">28°C</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">Rain Chance</span>
                  <span className="font-medium text-[var(--color-success)]">10%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">Track Temp</span>
                  <span className="font-medium">42°C</span>
                </div>
              </div>
            </div>

            {/* Track Info */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <h4 className="font-semibold mb-4">Track Info</h4>
              <div className="mb-4">
                <div className="text-xs text-[var(--color-text-secondary)] mb-1">Track Type</div>
                <div className="text-sm">High-speed circuit with long straights</div>
              </div>
              <div>
                <div className="text-xs text-[var(--color-text-secondary)] mb-2">Key Factors</div>
                <ul className="text-sm space-y-1">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">•</span>
                    <span>Tire management crucial</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">•</span>
                    <span>Overtaking opportunities</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">•</span>
                    <span>DRS zones effective</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
