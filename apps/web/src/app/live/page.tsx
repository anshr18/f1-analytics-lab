"use client";

import { useState } from "react";
import Link from "next/link";
import { BarChart3, Target, Gamepad2, MessageSquare, Radio } from "lucide-react";
import { LiveLeaderboard } from "@/components/live/LiveLeaderboard";
import { RacePicker } from "@/components/RacePicker";

export default function LivePage() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  const navItems = [
    { id: "predictions", label: "ML Predictions", icon: Target, href: "/predictions", active: false },
    { id: "dashboard", label: "Dashboard", icon: BarChart3, href: "/dashboard", active: false },
    { id: "strategy", label: "Strategy Simulator", icon: Gamepad2, href: "/strategy", active: false },
    { id: "live", label: "Live Timing", icon: Radio, href: "/live", active: true },
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
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <Radio className="w-8 h-8 text-f1red" />
            Live Timing
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time race data and leaderboard updates via WebSocket
          </p>
        </div>

        {/* Info Banner */}
        <div className="mb-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-1">
                Live WebSocket Streaming - Coming Soon
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-300">
                The WebSocket infrastructure is currently in development. For now, you can manually connect to view the leaderboard UI. Real-time updates will be available in a future release.
              </p>
            </div>
          </div>
        </div>

        {/* Race Picker */}
        <div className="mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Select Session</h2>
            <RacePicker onSessionSelect={setSelectedSessionId} />
          </div>
        </div>

        {/* Live Leaderboard */}
        {selectedSessionId ? (
          <LiveLeaderboard sessionId={selectedSessionId} autoConnect={false} />
        ) : (
          <div className="bg-gradient-to-br from-f1red to-red-700 text-white rounded-lg p-12 text-center">
            <Radio className="w-16 h-16 mx-auto mb-4 opacity-90" />
            <h2 className="text-2xl font-bold mb-2">No Session Selected</h2>
            <p className="text-lg opacity-90 mb-6">
              Select a race session above to start receiving live timing data
            </p>
            <div className="bg-white/10 rounded-lg p-6 max-w-2xl mx-auto">
              <h3 className="font-semibold mb-3">Features:</h3>
              <ul className="space-y-2 text-left">
                <li className="flex items-start gap-2">
                  <span className="text-xl">•</span>
                  <span>Real-time position updates via WebSocket</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-xl">•</span>
                  <span>Live lap times and sector splits</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-xl">•</span>
                  <span>Gap and interval tracking</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-xl">•</span>
                  <span>Session status and race control messages</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {/* Information Panel */}
        <div className="mt-8 bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">About Live Timing</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-700 dark:text-gray-300">
            <div>
              <h4 className="font-medium mb-2">How it works</h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>WebSocket connection for real-time updates</li>
                <li>Data sourced from OpenF1 API</li>
                <li>Automatic reconnection on connection loss</li>
                <li>Low-latency updates (~ 1 second)</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Data shown</h4>
              <ul className="space-y-1 list-disc list-inside">
                <li>Driver positions and gaps</li>
                <li>Lap times and sector splits</li>
                <li>Session and track status</li>
                <li>Pit stops and race events</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
