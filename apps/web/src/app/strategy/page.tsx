"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Target,
  BarChart3,
  Gamepad2,
  MessageSquare,
  Radio,
  Sparkles,
  TrendingUp,
  Flag,
  Zap,
  Timer,
  Trophy,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  MapPin,
  Calendar,
  CalendarDays,
  Info,
} from "lucide-react";
import { calculateUndercut } from "@/lib/api/strategy";
import { fetchSessions } from "@/lib/api/sessions";
import type { Session } from "@/types/api";
import type { UndercutResponse } from "@/types/strategy";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  BarChart,
  Bar,
  Cell,
  RadialBarChart,
  RadialBar,
  ReferenceLine,
} from "recharts";
import { motion } from "framer-motion";
import SafetyCarStrategy from "@/components/strategy/SafetyCarStrategy";
import RaceSimulation from "@/components/strategy/RaceSimulation";
import { Shield } from "lucide-react";

export default function StrategyPage() {
  const [activeTab, setActiveTab] = useState<"undercut" | "safety-car" | "race-sim">("undercut");
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<UndercutResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);

  // Form state
  const [sessionId, setSessionId] = useState("");
  const [attackingDriver, setAttackingDriver] = useState("VER");
  const [defendingDriver, setDefendingDriver] = useState("LEC");
  const [currentLap, setCurrentLap] = useState(25);
  const [gapSeconds, setGapSeconds] = useState(3.5);
  const [tyreAgeAttacker, setTyreAgeAttacker] = useState(15);
  const [tyreAgeDefender, setTyreAgeDefender] = useState(12);
  const [attackerCompound, setAttackerCompound] = useState("SOFT");
  const [defenderCompound, setDefenderCompound] = useState("MEDIUM");
  const [trackStatus, setTrackStatus] = useState("GREEN");

  const navItems = [
    {
      id: "predictions",
      label: "ML Predictions",
      icon: Target,
      href: "/predictions",
      active: false,
    },
    {
      id: "dashboard",
      label: "Dashboard",
      icon: BarChart3,
      href: "/dashboard",
      active: false,
    },
    {
      id: "strategy",
      label: "Strategy Simulator",
      icon: Gamepad2,
      href: "/strategy",
      active: true,
    },
    {
      id: "live",
      label: "Live Timing",
      icon: Radio,
      href: "/live",
      active: false,
    },
    {
      id: "assistant",
      label: "AI Assistant",
      icon: MessageSquare,
      href: "/assistant",
      active: false,
    },
  ];

  // Load sessions on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const sessionsData = await fetchSessions(undefined, true);
        setSessions(sessionsData);
        if (sessionsData.length > 0) {
          setSessionId(sessionsData[0].id);
        }
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    };
    loadSessions();
  }, []);

  const handleCalculate = async () => {
    setCalculating(true);
    setError(null);

    try {
      const response = await calculateUndercut({
        session_id: sessionId,
        attacking_driver: attackingDriver,
        defending_driver: defendingDriver,
        current_lap: currentLap,
        gap_seconds: gapSeconds,
        tyre_age_attacker: tyreAgeAttacker,
        tyre_age_defender: tyreAgeDefender,
        attacker_compound: attackerCompound,
        defender_compound: defenderCompound,
        track_status: trackStatus,
      });

      setResult(response);
    } catch (err: any) {
      console.error("Strategy calculation failed:", err);
      setError(
        err.message || "Failed to calculate strategy. Please try again."
      );
    } finally {
      setCalculating(false);
    }
  };

  // Determine verdict styling based on success probability
  const getVerdictConfig = (probability: number) => {
    if (probability > 0.7) {
      return {
        icon: CheckCircle2,
        color: "text-green-400",
        bgColor: "bg-green-900/20",
        borderColor: "border-green-700/30",
        title: "UNDERCUT RECOMMENDED",
        message: "High probability of gaining position",
      };
    } else if (probability > 0.4) {
      return {
        icon: AlertTriangle,
        color: "text-yellow-400",
        bgColor: "bg-yellow-900/20",
        borderColor: "border-yellow-700/30",
        title: "UNDERCUT RISKY",
        message: "Moderate probability - situational call",
      };
    } else {
      return {
        icon: XCircle,
        color: "text-red-400",
        bgColor: "bg-red-900/20",
        borderColor: "border-red-700/30",
        title: "UNDERCUT NOT RECOMMENDED",
        message: "Low probability of success",
      };
    }
  };

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
                    ${item.disabled ? "opacity-40 cursor-not-allowed" : ""}
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

      {/* Strategy Tabs */}
      <div className="border-b border-[var(--color-border)]">
        <div className="flex gap-1 px-6">
          <button
            onClick={() => setActiveTab("undercut")}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative
              ${
                activeTab === "undercut"
                  ? "text-[var(--color-primary)]"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }
            `}
          >
            <Zap className="w-4 h-4" />
            <span>Undercut Predictor</span>
            {activeTab === "undercut" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("safety-car")}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative
              ${
                activeTab === "safety-car"
                  ? "text-[var(--color-primary)]"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }
            `}
          >
            <Shield className="w-4 h-4" />
            <span>Safety Car Strategy</span>
            {activeTab === "safety-car" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("race-sim")}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative
              ${
                activeTab === "race-sim"
                  ? "text-[var(--color-primary)]"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }
            `}
          >
            <Flag className="w-4 h-4" />
            <span>Race Simulation</span>
            {activeTab === "race-sim" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]" />
            )}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {activeTab === "race-sim" ? (
          <RaceSimulation sessionId={sessionId} />
        ) : activeTab === "safety-car" ? (
          <SafetyCarStrategy sessionId={sessionId} />
        ) : (
          <div className="grid grid-cols-12 gap-6">
            {/* Left Column - Strategy Info */}
            <div className="col-span-3 space-y-4">
              {/* Strategy Type Card */}
              <div className="bg-[var(--color-surface)] rounded-xl border-2 border-[var(--color-primary)] p-4">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-lg bg-purple-500">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                </div>
                <h3 className="text-base font-semibold mt-3 mb-2">
                  Undercut/Overcut Predictor
                </h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-3">
                Simulates pit stop scenarios to determine optimal timing for
                undercut attempts
              </p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-[var(--color-background)] rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-purple-500"
                    style={{ width: "94%" }}
                  />
                </div>
                <span className="text-sm font-semibold text-[var(--color-success)]">
                  94%
                </span>
              </div>
            </div>

            {/* How It Works */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <div className="flex items-center gap-2 mb-4">
                <Info className="w-4 h-4 text-[var(--color-info)]" />
                <h4 className="font-semibold text-sm">How It Works</h4>
              </div>
              <ul className="text-sm space-y-2 text-[var(--color-text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">1.</span>
                  <span>Simulates 10 pit lap scenarios</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">2.</span>
                  <span>Uses ML lap time model for predictions</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">3.</span>
                  <span>Accounts for pit loss & tire warm-up</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">4.</span>
                  <span>Calculates success probability</span>
                </li>
              </ul>
            </div>

            {/* Strategy Stats */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <h4 className="font-semibold mb-4">Key Factors</h4>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Pit Loss Time
                  </span>
                  <span className="font-medium">~22.0s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Tire Warm-up
                  </span>
                  <span className="font-medium">2 laps</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Warm-up Penalty
                  </span>
                  <span className="font-medium">0.5s/lap</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Response Time
                  </span>
                  <span className="font-medium">3 laps</span>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Column - Calculator & Results */}
          <div className="col-span-6 space-y-6">
            {/* Strategy Calculator */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
              <div className="flex items-center gap-3 mb-6">
                <Sparkles className="w-5 h-5 text-[var(--color-primary)]" />
                <div>
                  <h3 className="text-lg font-semibold">Strategy Calculator</h3>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    Configure race scenario parameters
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                {/* Session Selection */}
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Session
                  </label>
                  <select
                    value={sessionId}
                    onChange={(e) => setSessionId(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  >
                    {sessions.map((session) => (
                      <option key={session.id} value={session.id}>
                        {session.session_type} -{" "}
                        {new Date(session.session_date).toLocaleDateString()}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Driver Selection */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Attacking Driver
                    </label>
                    <select
                      value={attackingDriver}
                      onChange={(e) => setAttackingDriver(e.target.value)}
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    >
                      <option value="VER">Max Verstappen (VER)</option>
                      <option value="LEC">Charles Leclerc (LEC)</option>
                      <option value="HAM">Lewis Hamilton (HAM)</option>
                      <option value="NOR">Lando Norris (NOR)</option>
                      <option value="SAI">Carlos Sainz (SAI)</option>
                      <option value="PER">Sergio Perez (PER)</option>
                      <option value="RUS">George Russell (RUS)</option>
                      <option value="ALO">Fernando Alonso (ALO)</option>
                      <option value="PIA">Oscar Piastri (PIA)</option>
                      <option value="STR">Lance Stroll (STR)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Defending Driver
                    </label>
                    <select
                      value={defendingDriver}
                      onChange={(e) => setDefendingDriver(e.target.value)}
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    >
                      <option value="LEC">Charles Leclerc (LEC)</option>
                      <option value="VER">Max Verstappen (VER)</option>
                      <option value="HAM">Lewis Hamilton (HAM)</option>
                      <option value="NOR">Lando Norris (NOR)</option>
                      <option value="SAI">Carlos Sainz (SAI)</option>
                      <option value="PER">Sergio Perez (PER)</option>
                      <option value="RUS">George Russell (RUS)</option>
                      <option value="ALO">Fernando Alonso (ALO)</option>
                      <option value="PIA">Oscar Piastri (PIA)</option>
                      <option value="STR">Lance Stroll (STR)</option>
                    </select>
                  </div>
                </div>

                {/* Race Conditions */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Current Lap
                    </label>
                    <input
                      type="number"
                      value={currentLap}
                      onChange={(e) => setCurrentLap(Number(e.target.value))}
                      min="1"
                      max="70"
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Gap (seconds)
                    </label>
                    <input
                      type="number"
                      value={gapSeconds}
                      onChange={(e) => setGapSeconds(Number(e.target.value))}
                      step="0.1"
                      min="0.1"
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                  </div>
                </div>

                {/* Tire Ages */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Attacker Tire Age (laps)
                    </label>
                    <input
                      type="number"
                      value={tyreAgeAttacker}
                      onChange={(e) =>
                        setTyreAgeAttacker(Number(e.target.value))
                      }
                      min="0"
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Defender Tire Age (laps)
                    </label>
                    <input
                      type="number"
                      value={tyreAgeDefender}
                      onChange={(e) =>
                        setTyreAgeDefender(Number(e.target.value))
                      }
                      min="0"
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    />
                  </div>
                </div>

                {/* Tire Compounds */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Attacker Compound
                    </label>
                    <select
                      value={attackerCompound}
                      onChange={(e) => setAttackerCompound(e.target.value)}
                      className="w-full px-4 py-2.5 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    >
                      <option value="SOFT">SOFT</option>
                      <option value="MEDIUM">MEDIUM</option>
                      <option value="HARD">HARD</option>
                      <option value="INTERMEDIATE">INTERMEDIATE</option>
                      <option value="WET">WET</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                      Defender Compound
                    </label>
                    <select
                      value={defenderCompound}
                      onChange={(e) => setDefenderCompound(e.target.value)}
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

                {/* Track Status */}
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

                {error && (
                  <div className="p-4 bg-red-900/20 border border-red-700/30 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <button
                  onClick={handleCalculate}
                  disabled={calculating || !sessionId}
                  className="w-full py-3.5 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/20"
                >
                  <Zap className="w-4 h-4" />
                  {calculating ? "Calculating..." : "Calculate Strategy"}
                </button>
              </div>
            </div>

            {/* Strategy Results */}
            {result ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                {/* Main Result Card */}
                <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <Trophy className="w-5 h-5 text-[var(--color-primary)]" />
                    <h3 className="text-lg font-semibold">Strategy Results</h3>
                  </div>

                  {/* Verdict */}
                  {(() => {
                    const verdict = getVerdictConfig(result.success_probability);
                    const VerdictIcon = verdict.icon;
                    return (
                      <div
                        className={`${verdict.bgColor} border ${verdict.borderColor} rounded-xl p-6 mb-6`}
                      >
                        <div className="flex items-center gap-3 mb-4">
                          <VerdictIcon className={`w-8 h-8 ${verdict.color}`} />
                          <div>
                            <div
                              className={`text-xl font-bold ${verdict.color}`}
                            >
                              {verdict.title}
                            </div>
                            <div className="text-sm text-[var(--color-text-secondary)]">
                              {verdict.message}
                            </div>
                          </div>
                        </div>

                        {/* Success Probability Meter */}
                        <div className="mt-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-[var(--color-text-secondary)]">
                              Success Probability
                            </span>
                            <span className={`text-2xl font-bold ${verdict.color}`}>
                              {(result.success_probability * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="bg-[var(--color-background)] rounded-full h-3">
                            <div
                              className={`h-3 rounded-full transition-all duration-1000 ${
                                result.success_probability > 0.7
                                  ? "bg-green-400"
                                  : result.success_probability > 0.4
                                  ? "bg-yellow-400"
                                  : "bg-red-400"
                              }`}
                              style={{
                                width: `${result.success_probability * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Strategy Details Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-[var(--color-background)] rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Flag className="w-4 h-4 text-[var(--color-info)]" />
                        <span className="text-sm text-[var(--color-text-secondary)]">
                          Optimal Pit Lap
                        </span>
                      </div>
                      <div className="text-2xl font-bold">
                        Lap {result.optimal_pit_lap}
                      </div>
                    </div>

                    <div className="bg-[var(--color-background)] rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Timer className="w-4 h-4 text-[var(--color-info)]" />
                        <span className="text-sm text-[var(--color-text-secondary)]">
                          Time Delta
                        </span>
                      </div>
                      <div
                        className={`text-2xl font-bold ${
                          result.time_delta > 0
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {result.time_delta > 0 ? "+" : ""}
                        {result.time_delta.toFixed(2)}s
                      </div>
                    </div>

                    <div className="bg-[var(--color-background)] rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-[var(--color-info)]" />
                        <span className="text-sm text-[var(--color-text-secondary)]">
                          Attacker Outlap
                        </span>
                      </div>
                      <div className="text-2xl font-bold">
                        {result.attacker_outlap.toFixed(3)}s
                      </div>
                    </div>

                    <div className="bg-[var(--color-background)] rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Flag className="w-4 h-4 text-[var(--color-info)]" />
                        <span className="text-sm text-[var(--color-text-secondary)]">
                          Defender Response
                        </span>
                      </div>
                      <div className="text-2xl font-bold">
                        Lap {result.defender_response_lap}
                      </div>
                    </div>
                  </div>

                  {/* Final Positions */}
                  <div className="mb-6">
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                      <Trophy className="w-4 h-4 text-[var(--color-warning)]" />
                      Predicted Final Positions
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(result.net_positions)
                        .sort(([, posA], [, posB]) => posA - posB)
                        .map(([driver, position]) => {
                          const isWinner = driver === attackingDriver && position === 1;
                          return (
                            <div
                              key={driver}
                              className={`flex items-center justify-between p-3 rounded-lg ${
                                isWinner
                                  ? "bg-green-900/20 border border-green-700/30"
                                  : "bg-[var(--color-background)]"
                              }`}
                            >
                              <div className="flex items-center gap-3">
                                {isWinner && (
                                  <Trophy className="w-4 h-4 text-[var(--color-warning)]" />
                                )}
                                <span className="font-mono text-lg font-bold">
                                  P{position}
                                </span>
                                <span className="font-medium">{driver}</span>
                              </div>
                              {driver === attackingDriver && (
                                <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                                  Attacker
                                </span>
                              )}
                              {driver === defendingDriver && (
                                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                                  Defender
                                </span>
                              )}
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  {/* Radial Success Chart */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6"
                  >
                    <div className="text-sm font-semibold mb-4">
                      Success Probability Meter
                    </div>
                    <ResponsiveContainer width="100%" height={250}>
                      <RadialBarChart
                        cx="50%"
                        cy="50%"
                        innerRadius="60%"
                        outerRadius="90%"
                        barSize={20}
                        data={[
                          {
                            name: "Success",
                            value: result.success_probability * 100,
                            fill:
                              result.success_probability > 0.7
                                ? "#10b981"
                                : result.success_probability > 0.4
                                ? "#f59e0b"
                                : "#ef4444",
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
                          fill={
                            result.success_probability > 0.7
                              ? "#10b981"
                              : result.success_probability > 0.4
                              ? "#f59e0b"
                              : "#ef4444"
                          }
                        >
                          {(result.success_probability * 100).toFixed(1)}%
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
                  </motion.div>
                </div>

                {/* Lap-by-Lap Analysis */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />
                    <h3 className="text-lg font-semibold">
                      Lap-by-Lap Analysis
                    </h3>
                  </div>

                  {/* Gap Evolution Chart */}
                  <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6 mb-6">
                    <div className="text-sm font-semibold mb-4">
                      Gap Evolution
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart
                        data={result.lap_by_lap}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <defs>
                          <linearGradient
                            id="colorGap"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="5%"
                              stopColor="#8b5cf6"
                              stopOpacity={0.8}
                            />
                            <stop
                              offset="95%"
                              stopColor="#8b5cf6"
                              stopOpacity={0.1}
                            />
                          </linearGradient>
                        </defs>
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
                          stroke="#a3a3a3"
                          label={{
                            value: "Gap (seconds)",
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
                          formatter={(value: any) => [
                            `${value.toFixed(2)}s`,
                            "Gap",
                          ]}
                        />
                        <ReferenceLine
                          y={0}
                          stroke="#ef4444"
                          strokeDasharray="3 3"
                          label={{
                            value: "Position Change",
                            fill: "#ef4444",
                            fontSize: 12,
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="cumulative_gap"
                          stroke="#8b5cf6"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#colorGap)"
                        />
                        <Line
                          type="monotone"
                          dataKey="cumulative_gap"
                          stroke="#8b5cf6"
                          strokeWidth={3}
                          dot={{ fill: "#8b5cf6", r: 4 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Lap Time Comparison Chart */}
                  <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6">
                    <div className="text-sm font-semibold mb-4">
                      Lap Time Comparison
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart
                        data={result.lap_by_lap.slice(0, 10)}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                        <XAxis dataKey="lap" stroke="#a3a3a3" />
                        <YAxis
                          stroke="#a3a3a3"
                          label={{
                            value: "Lap Time (s)",
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
                          formatter={(value: any) => `${value.toFixed(3)}s`}
                        />
                        <Line
                          type="monotone"
                          dataKey="attacker_lap_time"
                          stroke="#8b5cf6"
                          strokeWidth={2}
                          name={attackingDriver}
                          dot={{ fill: "#8b5cf6", r: 4 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="defender_lap_time"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          name={defendingDriver}
                          dot={{ fill: "#3b82f6", r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>
              </motion.div>
            ) : (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-12 text-center">
                <div className="w-16 h-16 bg-[var(--color-primary)]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Gamepad2 className="w-8 h-8 text-[var(--color-primary)]" />
                </div>
                <h3 className="text-lg font-semibold mb-2">
                  No strategy calculated yet
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Configure the race scenario and click &quot;Calculate
                  Strategy&quot;
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Info Cards */}
          <div className="col-span-3 space-y-4">
            {/* Current Session Info */}
            {sessions.length > 0 && sessionId && (
              <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
                <div className="flex items-center gap-2 mb-4">
                  <CalendarDays className="w-4 h-4 text-[var(--color-primary)]" />
                  <h4 className="font-semibold text-sm">Selected Session</h4>
                </div>
                {(() => {
                  const currentSession = sessions.find((s) => s.id === sessionId);
                  if (!currentSession) return null;
                  return (
                    <>
                      <h3 className="text-xl font-bold mb-2">
                        {currentSession.session_type}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] mb-4">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>{currentSession.location || "Unknown"}</span>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                            <Calendar className="w-3.5 h-3.5" />
                            <span>Date</span>
                          </div>
                          <span className="font-medium">
                            {new Date(
                              currentSession.session_date
                            ).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            )}

            {/* Strategy Tips */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <h4 className="font-semibold mb-4">Strategy Tips</h4>
              <ul className="text-sm space-y-2 text-[var(--color-text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">•</span>
                  <span>Larger tire age gap favors undercut</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">•</span>
                  <span>Smaller gaps increase success probability</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">•</span>
                  <span>Fresh soft tires provide maximum advantage</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[var(--color-primary)]">•</span>
                  <span>Consider track position vs tire strategy</span>
                </li>
              </ul>
            </div>

            {/* Performance Metrics */}
            <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
              <h4 className="font-semibold mb-4">Calculation Details</h4>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Scenarios Tested
                  </span>
                  <span className="font-medium">10</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    ML Model
                  </span>
                  <span className="font-medium">Lap Time v1.0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-text-secondary)]">
                    Simulation Type
                  </span>
                  <span className="font-medium">Undercut</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
