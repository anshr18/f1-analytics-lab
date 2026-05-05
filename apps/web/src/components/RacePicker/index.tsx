"use client";

import { useState, useEffect } from "react";
import { fetchSeasons, fetchEvents } from "@/lib/api/races";
import { fetchSessions } from "@/lib/api/sessions";
import { ingestSession, getTaskStatus } from "@/lib/api/ingest";
import type { Season, Event, Session } from "@/types/api";

interface RacePickerProps {
  onSessionSelect: (sessionId: string) => void;
}

export function RacePicker({ onSessionSelect }: RacePickerProps) {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);

  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [ingestProgress, setIngestProgress] = useState(0);
  const [ingestMessage, setIngestMessage] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { loadSeasons(); }, []);
  useEffect(() => {
    if (selectedYear) { loadEvents(selectedYear); }
    else { setEvents([]); setSelectedEvent(null); }
  }, [selectedYear]);
  useEffect(() => {
    if (selectedEvent) { loadSessions(selectedEvent); }
    else { setSessions([]); setSelectedSession(null); }
  }, [selectedEvent]);

  async function loadSeasons() {
    try {
      setLoading(true);
      const data = await fetchSeasons();
      setSeasons(data);
      if (data.length > 0) setSelectedYear(data[0].year);
    } catch { setError("Failed to load seasons"); }
    finally { setLoading(false); }
  }

  async function loadEvents(year: number) {
    try {
      setLoading(true);
      const data = await fetchEvents(year);
      setEvents(data);
    } catch { setError("Failed to load events"); }
    finally { setLoading(false); }
  }

  async function loadSessions(eventId: string) {
    try {
      setLoading(true);
      const data = await fetchSessions(eventId);
      setSessions(data);
    } catch { setError("Failed to load sessions"); }
    finally { setLoading(false); }
  }

  async function handleLoad() {
    if (!selectedEvent || !selectedSession) return;
    const event = events.find((e) => e.id === selectedEvent);
    const session = sessions.find((s) => s.id === selectedSession);
    if (!event || !session) return;

    if (session.is_ingested) {
      onSessionSelect(selectedSession);
      return;
    }

    try {
      setIngesting(true);
      setIngestProgress(0);
      setIngestMessage("Starting ingestion...");
      setError(null);

      const response = await ingestSession({
        year: event.season_year,
        round_number: event.round_number,
        session_type: session.session_type,
        source: "fastf1",
      });

      const taskId = response.task_id;
      let completed = false;
      while (!completed) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const status = await getTaskStatus(taskId);
        setIngestProgress(status.progress || 0);
        setIngestMessage(status.current || "Processing...");
        if (status.status === "SUCCESS") {
          completed = true;
          setIngestProgress(100);
          setIngestMessage("Ingestion complete!");
          await loadSessions(selectedEvent);
          if (status.session_id) onSessionSelect(status.session_id);
        } else if (status.status === "FAILURE") {
          throw new Error(status.error || "Ingestion failed");
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  }

  const canLoad = selectedEvent && selectedSession;
  const selectedSessionData = sessions.find((s) => s.id === selectedSession);

  return (
    <div className="bg-surface border border-surface-container-high h-full flex flex-col">
      {/* Header */}
      <div className="px-md py-sm border-b border-surface-container-high flex items-center gap-sm bg-surface-container-lowest">
        <span className="material-symbols-outlined text-on-surface-variant text-[16px]">tune</span>
        <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
          Session Configuration
        </span>
      </div>

      {/* Controls */}
      <div className="flex-1 overflow-y-auto p-md flex flex-col gap-lg">
        {/* Season */}
        <div className="flex flex-col gap-xs">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Season</label>
          <div className="relative">
            <select
              value={selectedYear || ""}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              disabled={loading}
              className="w-full bg-surface-container-lowest border border-surface-container-high text-on-surface font-data-sm text-data-sm h-10 pl-md pr-8 appearance-none cursor-pointer hover:border-secondary-container focus:outline-none focus:border-primary-container transition-colors disabled:opacity-50"
            >
              <option value="">Select season</option>
              {seasons.map((s) => (
                <option key={s.year} value={s.year}>{s.year}</option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px] pointer-events-none">
              arrow_drop_down
            </span>
          </div>
        </div>

        {/* Grand Prix */}
        <div className="flex flex-col gap-xs">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Grand Prix</label>
          <div className="relative">
            <select
              value={selectedEvent || ""}
              onChange={(e) => setSelectedEvent(e.target.value)}
              disabled={loading || !selectedYear}
              className="w-full bg-surface-container-lowest border border-surface-container-high text-on-surface font-data-sm text-data-sm h-10 pl-md pr-8 appearance-none cursor-pointer hover:border-secondary-container focus:outline-none focus:border-primary-container transition-colors disabled:opacity-50"
            >
              <option value="">Select race</option>
              {events.map((e) => (
                <option key={e.id} value={e.id}>
                  Rnd {e.round_number}: {e.event_name}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px] pointer-events-none">
              arrow_drop_down
            </span>
          </div>
        </div>

        {/* Session */}
        <div className="flex flex-col gap-xs">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Session</label>
          <div className="relative">
            <select
              value={selectedSession || ""}
              onChange={(e) => setSelectedSession(e.target.value)}
              disabled={loading || !selectedEvent}
              className="w-full bg-surface-container-lowest border border-surface-container-high text-on-surface font-data-sm text-data-sm h-10 pl-md pr-8 appearance-none cursor-pointer hover:border-secondary-container focus:outline-none focus:border-primary-container transition-colors disabled:opacity-50"
            >
              <option value="">Select session</option>
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.session_type}{s.is_ingested ? " ✓" : ""}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px] pointer-events-none">
              arrow_drop_down
            </span>
          </div>
        </div>

        {/* Ingestion progress */}
        {ingesting && (
          <div className="flex flex-col gap-sm">
            <div className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-primary-container text-[14px] animate-spin">
                refresh
              </span>
              <span className="font-label-caps text-label-caps text-on-surface-variant">
                {ingestMessage}
              </span>
            </div>
            <div className="w-full bg-surface-container-high h-0.5">
              <div
                className="bg-primary-container h-0.5 transition-all duration-300"
                style={{ width: `${ingestProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="border border-error-container bg-error-container/10 px-sm py-xs">
            <span className="font-data-sm text-data-sm text-error">{error}</span>
          </div>
        )}
      </div>

      {/* CTA */}
      <div className="p-md border-t border-surface-container-high bg-surface-container-lowest">
        <button
          onClick={handleLoad}
          disabled={!canLoad || ingesting}
          className="w-full bg-primary-container text-on-primary-container font-label-caps text-label-caps h-10 uppercase tracking-widest flex items-center justify-center gap-sm hover:bg-inverse-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span className="material-symbols-outlined text-[16px]">memory</span>
          {ingesting
            ? "Ingesting..."
            : selectedSessionData?.is_ingested
            ? "Load Telemetry"
            : "Initialize Telemetry"}
        </button>
      </div>
    </div>
  );
}
