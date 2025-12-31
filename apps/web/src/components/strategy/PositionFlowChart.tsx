"use client";

import { motion } from "framer-motion";
import { ArrowRight, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { SafetyCarDecision } from "@/types/strategy";

interface PositionFlowChartProps {
  decisions: SafetyCarDecision[];
}

export default function PositionFlowChart({ decisions }: PositionFlowChartProps) {
  // Sort by current position
  const sortedDecisions = [...decisions].sort(
    (a, b) => a.current_position - b.current_position
  );

  return (
    <div className="space-y-3">
      {sortedDecisions.map((decision, idx) => {
        const posChange = decision.predicted_position_if_pit - decision.current_position;
        const Icon =
          posChange < 0 ? TrendingUp : posChange > 0 ? TrendingDown : Minus;
        const changeColor =
          posChange < 0
            ? "text-green-400"
            : posChange > 0
            ? "text-red-400"
            : "text-gray-400";

        return (
          <motion.div
            key={decision.driver_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
            className="flex items-center gap-4 p-3 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)]"
          >
            {/* Current Position */}
            <div className="flex items-center gap-2 w-24">
              <span className="font-mono text-lg font-bold">
                P{decision.current_position}
              </span>
              <span className="text-sm font-bold">{decision.driver_id}</span>
            </div>

            {/* Arrow */}
            <ArrowRight className="w-5 h-5 text-[var(--color-text-secondary)]" />

            {/* Decision Badge */}
            <div
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                decision.recommendation === "PIT"
                  ? "bg-green-500/20 text-green-400"
                  : decision.recommendation === "STAY_OUT"
                  ? "bg-blue-500/20 text-blue-400"
                  : "bg-yellow-500/20 text-yellow-400"
              }`}
            >
              {decision.recommendation.replace("_", " ")}
            </div>

            {/* Position Change */}
            <div className="flex items-center gap-2 ml-auto">
              {posChange !== 0 && (
                <>
                  <Icon className={`w-4 h-4 ${changeColor}`} />
                  <span className={`text-sm font-bold ${changeColor}`}>
                    {Math.abs(posChange)} {Math.abs(posChange) === 1 ? "place" : "places"}
                  </span>
                </>
              )}
              {posChange === 0 && (
                <span className="text-sm text-gray-400">No change</span>
              )}
            </div>

            {/* New Position */}
            <ArrowRight className="w-5 h-5 text-[var(--color-text-secondary)]" />
            <div className="w-16">
              <span className={`font-mono text-lg font-bold ${changeColor}`}>
                P{decision.predicted_position_if_pit}
              </span>
            </div>

            {/* Confidence */}
            <div className="w-20">
              <div className="text-xs text-[var(--color-text-secondary)] mb-1">
                {(decision.confidence * 100).toFixed(0)}%
              </div>
              <div className="bg-[var(--color-surface)] rounded-full h-1">
                <div
                  className={`h-1 rounded-full ${
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
          </motion.div>
        );
      })}
    </div>
  );
}
