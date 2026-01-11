"use client";

import { useState } from "react";
import Link from "next/link";
import { BarChart3, Target, Gamepad2, MessageSquare, Radio } from "lucide-react";
import { RacePicker } from "@/components/RacePicker";
import { LapChart } from "@/components/charts/LapChart";
import { StintChart } from "@/components/charts/StintChart";
import { PredictionSummaryCard } from "@/components/predictions/PredictionSummaryCard";

export default function DashboardPage() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  const navItems = [
    { id: "predictions", label: "ML Predictions", icon: Target, href: "/predictions", active: false },
    { id: "dashboard", label: "Dashboard", icon: BarChart3, href: "/dashboard", active: true },
    { id: "strategy", label: "Strategy Simulator", icon: Gamepad2, href: "/strategy", active: false },
    { id: "live", label: "Live Timing", icon: Radio, href: "/live", active: false },
    { id: "assistant", label: "AI Assistant", icon: MessageSquare, href: "/assistant", active: false },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)]">
      {/* Top Navigation */}
      <div className="border-b border-[var(--color-border)]">
        <div className="flex gap-1 px-6 pt-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`
                  relative px-4 py-3 text-sm font-medium transition-colors rounded-t-lg
                  ${
                    item.active
                      ? "text-[var(--color-primary)] bg-[var(--color-background)]"
                      : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]"
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.active && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]" />
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">F1 Analytics Dashboard</h1>
          <p className="text-[var(--color-text-secondary)]">Select a race and session to analyze lap times and tyre strategies</p>
        </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {/* Race Picker - Takes 1 column */}
        <div className="lg:col-span-1">
          <RacePicker onSessionSelect={setSelectedSessionId} />
        </div>

        {/* Instructions - Takes 2 columns */}
        {!selectedSessionId && (
          <div className="lg:col-span-2">
            <div className="bg-gradient-to-br from-f1red to-red-700 text-white rounded-lg p-8 h-full flex flex-col justify-center">
              <h2 className="text-2xl font-bold mb-4">Get Started</h2>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-white text-f1red rounded-full flex items-center justify-center font-bold">
                    1
                  </div>
                  <div>
                    <div className="font-semibold">Select a Season</div>
                    <div className="text-sm opacity-90">Choose from available F1 seasons</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-white text-f1red rounded-full flex items-center justify-center font-bold">
                    2
                  </div>
                  <div>
                    <div className="font-semibold">Pick a Grand Prix</div>
                    <div className="text-sm opacity-90">Select a race weekend from the calendar</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-white text-f1red rounded-full flex items-center justify-center font-bold">
                    3
                  </div>
                  <div>
                    <div className="font-semibold">Choose Session Type</div>
                    <div className="text-sm opacity-90">Practice, Qualifying, Sprint, or Race</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-white text-f1red rounded-full flex items-center justify-center font-bold">
                    4
                  </div>
                  <div>
                    <div className="font-semibold">Ingest & Load</div>
                    <div className="text-sm opacity-90">
                      Click the button to load data (first time will ingest from FastF1)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Charts - Only show when session is selected */}
      {selectedSessionId && (
        <div className="space-y-6">
          {/* ML Prediction Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <PredictionSummaryCard
              title="Expected Lap Time"
              modelName="lap_time"
              sessionId={selectedSessionId}
            />
            <PredictionSummaryCard
              title="Overtake Probability"
              modelName="overtake"
              sessionId={selectedSessionId}
            />
            <PredictionSummaryCard
              title="Predicted Winner"
              modelName="race_result"
              sessionId={selectedSessionId}
            />
          </div>

          <LapChart sessionId={selectedSessionId} />
          <StintChart sessionId={selectedSessionId} />

          {/* Data Summary */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3">About This Data</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700 dark:text-gray-300">
              <div>
                <div className="font-medium mb-1">Lap Time Chart</div>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Shows lap time evolution throughout the session</li>
                  <li>Filters out pit laps and deleted laps</li>
                  <li>Each line represents a driver</li>
                  <li>Lower is faster</li>
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">Tyre Strategy</div>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Visualizes each driver's tyre stint</li>
                  <li>Colors represent compounds (Soft/Medium/Hard)</li>
                  <li>Bar length shows stint duration</li>
                  <li>Hover for detailed stint information</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
