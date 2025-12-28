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
} from "@/lib/api/predictions";

export default function PredictionsPage() {
  const [selectedModel, setSelectedModel] = useState<string | null>("race-result");
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  // Form state
  const [driver, setDriver] = useState("Charles Leclerc");
  const [gridPosition, setGridPosition] = useState(1);
  const [weather, setWeather] = useState("Dry");
  const [trackTemp, setTrackTemp] = useState(45);

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
    try {
      // Simulate prediction
      await new Promise(resolve => setTimeout(resolve, 1500));

      setPrediction({
        position: 1,
        confidence: 86.5,
        driver: driver,
        impactFactors: [
          { name: "Grid Position", impact: "+35%", positive: true },
          { name: "Weather Conditions", impact: "+25%", positive: true },
          { name: "Track Performance", impact: "+20%", positive: true },
          { name: "Car Setup", impact: "-20%", positive: false },
        ],
        modelAccuracy: "87.3%",
      });
    } catch (error) {
      console.error("Prediction failed:", error);
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
                <button
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setPrediction(null);
                  }}
                  className={`
                    w-full text-left p-4 rounded-xl border-2 transition-all
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
                    <button
                      className="ml-auto p-1 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]"
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                    >
                      ×
                    </button>
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
                </button>
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

              {/* Model Features */}
              <div className="mb-6">
                <h4 className="text-sm font-medium text-[var(--color-text-secondary)] mb-3">
                  Model Features
                </h4>
                <div className="flex flex-wrap gap-2">
                  {["Grid Position", "Weather", "Track History", "Car Performance"].map((feature) => (
                    <span
                      key={feature}
                      className="px-3 py-1.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text-secondary)]"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>

              {/* Form Fields */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Driver
                  </label>
                  <select
                    value={driver}
                    onChange={(e) => setDriver(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  >
                    <option>Charles Leclerc</option>
                    <option>Max Verstappen</option>
                    <option>Lewis Hamilton</option>
                    <option>Lando Norris</option>
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
                      Weather
                    </label>
                    <select
                      value={weather}
                      onChange={(e) => setWeather(e.target.value)}
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    >
                      <option>Dry</option>
                      <option>Wet</option>
                      <option>Mixed</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Track Temperature (°C)
                  </label>
                  <input
                    type="number"
                    value={trackTemp}
                    onChange={(e) => setTrackTemp(Number(e.target.value))}
                    placeholder="e.g., 45"
                    className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  />
                </div>

                <button
                  onClick={handlePredict}
                  disabled={predicting}
                  className="w-full py-3.5 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4" />
                  {predicting ? "Generating..." : "Generate Prediction"}
                </button>
              </div>
            </div>

            {/* Prediction Results */}
            {prediction ? (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
                <div className="flex items-center gap-3 mb-6">
                  <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />
                  <h3 className="text-lg font-semibold">Prediction Results</h3>
                </div>

                {/* Primary Prediction */}
                <div className="bg-gradient-to-br from-green-900/20 to-green-800/10 border border-green-700/30 rounded-xl p-6 mb-6">
                  <div className="text-sm text-green-400 mb-2">Primary Prediction</div>
                  <div className="text-6xl font-bold text-green-400 mb-2">
                    P{prediction.position}
                  </div>
                  <div className="text-sm text-[var(--color-text-secondary)] mb-4">
                    Predicted Finish for {prediction.driver}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--color-text-secondary)]">Confidence</span>
                    <span className="text-lg font-semibold text-green-400">{prediction.confidence}%</span>
                  </div>
                  <div className="mt-2 bg-[var(--color-background)] rounded-full h-2">
                    <div
                      className="bg-green-400 h-2 rounded-full"
                      style={{ width: `${prediction.confidence}%` }}
                    />
                  </div>
                </div>

                {/* Impact Factors */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Info className="w-4 h-4 text-[var(--color-info)]" />
                    <h4 className="font-semibold">Impact Factors</h4>
                  </div>
                  <div className="space-y-3">
                    {prediction.impactFactors.map((factor: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="text-sm text-[var(--color-text-primary)]">{factor.name}</span>
                        <div className="flex items-center gap-3">
                          <div className={`w-24 h-1.5 rounded-full ${factor.positive ? 'bg-green-500' : 'bg-orange-500'}`} />
                          <span className={`text-sm font-semibold w-16 text-right ${factor.positive ? 'text-green-400' : 'text-orange-400'}`}>
                            {factor.impact}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Model Accuracy */}
                <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-4">
                  <div className="text-sm font-semibold mb-2">
                    Model Accuracy: {prediction.modelAccuracy}
                  </div>
                  <div className="text-xs text-[var(--color-text-secondary)]">
                    Based on analysis of 500+ races using 4 key parameters
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-12 text-center">
                <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-[var(--color-primary)]" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No predictions yet</h3>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Fill in the form and click &quot;Generate Prediction&quot;
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
