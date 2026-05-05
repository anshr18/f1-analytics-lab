"use client";

import { useState } from "react";
import { RacePicker } from "@/components/RacePicker";
import { LapChart } from "@/components/charts/LapChart";
import { StintChart } from "@/components/charts/StintChart";
import { PredictionSummaryCard } from "@/components/predictions/PredictionSummaryCard";

// ── Hero Stats Bar ────────────────────────────────────────────────────────────

function HeroStatsBar({ sessionId }: { sessionId: string | null }) {
  if (!sessionId) {
    return (
      <div className="bg-surface border-b border-surface-container-high h-[72px] shrink-0 flex items-center px-lg justify-between relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.06]"
          style={{ backgroundImage: "repeating-linear-gradient(45deg, transparent, transparent 10px, #2a2a2a 10px, #2a2a2a 20px)" }}
        />
        <div className="flex items-center gap-lg relative z-10">
          <span className="material-symbols-outlined text-surface-container-highest text-[40px]">sensors_off</span>
          <div>
            <h1 className="font-headline-md text-headline-md text-surface-container-highest uppercase tracking-widest leading-none">
              No Active Session
            </h1>
            <p className="font-label-caps text-label-caps text-surface-container-high mt-xs">
              Select a session from the control panel
            </p>
          </div>
        </div>
        <div className="flex gap-lg relative z-10 opacity-30 pointer-events-none">
          {["Air Temp", "Track Temp", "Status"].map((label, i) => (
            <div key={label} className={`flex flex-col items-end ${i < 2 ? "border-r border-surface-container-high pr-lg" : ""}`}>
              <span className="font-label-caps text-label-caps text-on-surface-variant">{label}</span>
              <span className="font-data-lg text-data-lg text-on-surface">{i === 2 ? "AWAITING" : "--.-°C"}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#141414] border-b border-[#2A2A2A] py-2 px-6 shrink-0 overflow-x-auto hide-scrollbar">
      <div className="flex items-center gap-6 font-data-sm text-data-sm text-secondary whitespace-nowrap">
        <div className="flex items-center gap-2">
          <span className="text-primary-container animate-pulse text-lg leading-none">●</span>
          <span className="font-data-lg text-data-lg text-on-surface">LIVE</span>
        </div>
        {[
          { label: "Leader", value: "VER" },
          { label: "Fastest", value: "HAM 1:21.432" },
          { label: "Gap", value: "+2.4s" },
          { label: "Lap", value: "42/70" },
          { label: "Track Temp", value: "34°C" },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center gap-2">
            <span className="text-[#2A2A2A]">|</span>
            <span className="text-on-surface-variant">{label.toUpperCase()}:</span>
            <span className="text-on-surface">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Awaiting State ────────────────────────────────────────────────────────────

function AwaitingState() {
  return (
    <div className="flex-1 grid grid-cols-12 grid-rows-2 gap-gutter relative bg-surface-container-lowest min-h-0">
      {/* Overlay */}
      <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none backdrop-blur-[2px]">
        <div className="bg-surface border border-surface-container-high p-xl flex flex-col items-center gap-md shadow-2xl relative overflow-hidden max-w-sm w-full">
          <div className="absolute top-0 left-0 w-full h-0.5 bg-primary-container" />
          <span className="material-symbols-outlined text-primary-container text-[48px]">query_stats</span>
          <h2 className="font-headline-md text-headline-md text-on-surface uppercase tracking-tight text-center">
            Awaiting Telemetry Input
          </h2>
          <p className="font-body-base text-body-base text-on-surface-variant text-center">
            Select a session parameter from the control panel to begin real-time data ingestion and analysis.
          </p>
        </div>
      </div>

      {/* Ghost panels */}
      <div className="col-span-12 lg:col-span-8 row-span-1 border border-surface-container-high bg-surface opacity-30 flex flex-col overflow-hidden">
        <div className="px-sm py-xs border-b border-surface-container-high flex items-center gap-sm">
          <div className="w-2 h-2 bg-surface-container-highest rounded-full" />
          <span className="font-label-caps text-label-caps text-surface-container-highest">Lap Time Evolution</span>
        </div>
        <div className="flex-1 p-lg flex flex-col gap-8 justify-end">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border-b border-dashed border-surface-container-high w-full h-px" />
          ))}
          <div className="border-b border-solid border-surface-container-highest w-full h-px mt-4" />
        </div>
      </div>

      <div className="col-span-12 lg:col-span-4 row-span-1 border border-surface-container-high bg-surface opacity-30 flex flex-col overflow-hidden">
        <div className="px-sm py-xs border-b border-surface-container-high flex items-center gap-sm">
          <div className="w-2 h-2 bg-surface-container-highest rounded-full" />
          <span className="font-label-caps text-label-caps text-surface-container-highest">Tyre Strategy</span>
        </div>
        <div className="flex-1 flex items-center justify-center p-xl">
          <div className="w-32 h-32 rounded-full border-[6px] border-dashed border-surface-container-highest" />
        </div>
      </div>

      <div className="col-span-12 row-span-1 border border-surface-container-high bg-surface opacity-30 flex flex-col overflow-hidden">
        <div className="px-sm py-xs border-b border-surface-container-high flex items-center gap-sm">
          <div className="w-2 h-2 bg-surface-container-highest rounded-full" />
          <span className="font-label-caps text-label-caps text-surface-container-highest">ML Predictions</span>
        </div>
        <div className="flex-1 p-md flex flex-col gap-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="w-full h-8 bg-surface-container-highest flex items-center px-md gap-4">
              <div className="h-2 w-8 bg-surface-container-high" />
              <div className="h-2 w-24 bg-surface-container-high" />
              <div className="h-2 w-12 bg-surface-container-high ml-auto" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Data Canvas ───────────────────────────────────────────────────────────────

function DataCanvas({ sessionId }: { sessionId: string }) {
  return (
    <div className="flex-1 flex flex-col gap-gutter min-h-0 overflow-y-auto">
      {/* ML Prediction Chips */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter shrink-0">
        <PredictionSummaryCard title="Expected Lap Time" modelName="lap_time" sessionId={sessionId} />
        <PredictionSummaryCard title="Overtake Probability" modelName="overtake" sessionId={sessionId} />
        <PredictionSummaryCard title="Predicted Finish" modelName="race_result" sessionId={sessionId} />
      </div>

      {/* Lap Time Chart */}
      <div className="bg-[#141414] border border-[#2A2A2A] flex flex-col shrink-0">
        <div className="px-md py-sm border-b border-[#2A2A2A]">
          <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Lap Time Evolution
          </span>
        </div>
        <div className="p-gutter">
          <LapChart sessionId={sessionId} />
        </div>
      </div>

      {/* Tyre Strategy Chart */}
      <div className="bg-[#141414] border border-[#2A2A2A] flex flex-col shrink-0">
        <div className="px-md py-sm border-b border-[#2A2A2A]">
          <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Tyre Strategy Projection
          </span>
        </div>
        <div className="p-gutter">
          <StintChart sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <HeroStatsBar sessionId={selectedSessionId} />

      {/* Main workspace */}
      <div className="flex flex-1 gap-gutter p-margin overflow-hidden">
        {/* Left panel: session selector */}
        <aside className="w-[220px] xl:w-[260px] shrink-0 flex flex-col h-full hidden md:flex">
          <RacePicker onSessionSelect={setSelectedSessionId} />
        </aside>

        {/* Right canvas */}
        <section className="flex-1 flex flex-col gap-gutter min-w-0 min-h-0">
          {/* Mobile race picker (above canvas on small screens) */}
          <div className="md:hidden">
            <RacePicker onSessionSelect={setSelectedSessionId} />
          </div>

          {!selectedSessionId ? (
            <AwaitingState />
          ) : (
            <DataCanvas sessionId={selectedSessionId} />
          )}
        </section>
      </div>
    </div>
  );
}
