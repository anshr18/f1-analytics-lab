"use client";

import { useState, useEffect } from "react";
import { fetchSeasons, fetchEvents } from "@/lib/api/races";
import { fetchSessions } from "@/lib/api/sessions";
import { ingestSession, getTaskStatus } from "@/lib/api/ingest";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
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

  // Load seasons on mount
  useEffect(() => {
    loadSeasons();
  }, []);

  // Load events when year changes
  useEffect(() => {
    if (selectedYear) {
      loadEvents(selectedYear);
    } else {
      setEvents([]);
      setSelectedEvent(null);
    }
  }, [selectedYear]);

  // Load sessions when event changes
  useEffect(() => {
    if (selectedEvent) {
      loadSessions(selectedEvent);
    } else {
      setSessions([]);
      setSelectedSession(null);
    }
  }, [selectedEvent]);

  async function loadSeasons() {
    try {
      setLoading(true);
      const data = await fetchSeasons();
      setSeasons(data);
      if (data.length > 0) {
        setSelectedYear(data[0].year); // Auto-select latest year
      }
    } catch (err) {
      setError("Failed to load seasons");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadEvents(year: number) {
    try {
      setLoading(true);
      const data = await fetchEvents(year);
      setEvents(data);
    } catch (err) {
      setError("Failed to load events");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadSessions(eventId: string) {
    try {
      setLoading(true);
      const data = await fetchSessions(eventId);
      setSessions(data);
    } catch (err) {
      setError("Failed to load sessions");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleIngestAndLoad() {
    if (!selectedEvent || !selectedSession) return;

    const event = events.find((e) => e.id === selectedEvent);
    const session = sessions.find((s) => s.id === selectedSession);

    if (!event || !session) return;

    // Check if already ingested
    if (session.is_ingested) {
      onSessionSelect(selectedSession);
      return;
    }

    try {
      setIngesting(true);
      setIngestProgress(0);
      setIngestMessage("Starting ingestion...");
      setError(null);

      // Start ingestion
      const response = await ingestSession({
        year: event.season_year,
        round_number: event.round_number,
        session_type: session.session_type,
        source: "fastf1",
      });

      // Poll for status
      const taskId = response.task_id;
      let completed = false;

      while (!completed) {
        await new Promise((resolve) => setTimeout(resolve, 2000)); // Poll every 2s

        const status = await getTaskStatus(taskId);

        setIngestProgress(status.progress || 0);
        setIngestMessage(status.current || "Processing...");

        if (status.status === "SUCCESS") {
          completed = true;
          setIngestProgress(100);
          setIngestMessage("Ingestion complete!");

          // Reload sessions to get updated is_ingested flag
          await loadSessions(selectedEvent);

          // Load the session
          if (status.session_id) {
            onSessionSelect(status.session_id);
          }
        } else if (status.status === "FAILURE") {
          throw new Error(status.error || "Ingestion failed");
        }
      }
    } catch (err: any) {
      setError(err.message || "Ingestion failed");
      console.error(err);
    } finally {
      setIngesting(false);
    }
  }

  const selectedEventData = events.find((e) => e.id === selectedEvent);
  const selectedSessionData = sessions.find((s) => s.id === selectedSession);
  const canIngest = selectedEvent && selectedSession;

  return (
    <Card title="Race Selection">
      <div className="space-y-4">
        {/* Year Selector */}
        <div>
          <label className="block text-sm font-medium mb-2">Season</label>
          <select
            value={selectedYear || ""}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700"
            disabled={loading}
          >
            <option value="">Select a season</option>
            {seasons.map((season) => (
              <option key={season.year} value={season.year}>
                {season.year} ({season.event_count || 0} events)
              </option>
            ))}
          </select>
        </div>

        {/* Event Selector */}
        <div>
          <label className="block text-sm font-medium mb-2">Grand Prix</label>
          <select
            value={selectedEvent || ""}
            onChange={(e) => setSelectedEvent(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700"
            disabled={loading || !selectedYear}
          >
            <option value="">Select a race</option>
            {events.map((event) => (
              <option key={event.id} value={event.id}>
                Round {event.round_number}: {event.event_name}
              </option>
            ))}
          </select>
        </div>

        {/* Session Selector */}
        <div>
          <label className="block text-sm font-medium mb-2">Session</label>
          <select
            value={selectedSession || ""}
            onChange={(e) => setSelectedSession(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700"
            disabled={loading || !selectedEvent}
          >
            <option value="">Select a session</option>
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.session_type} {session.is_ingested && "✓ (ingested)"}
              </option>
            ))}
          </select>
        </div>

        {/* Ingestion Status */}
        {ingesting && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Spinner size="sm" />
              <span className="font-medium">{ingestMessage}</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-f1red h-2 rounded-full transition-all duration-300"
                style={{ width: `${ingestProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Selection Summary */}
        {selectedEventData && selectedSessionData && !ingesting && (
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-sm">
            <div className="font-medium mb-2">Selected:</div>
            <div>
              {selectedYear} - {selectedEventData.event_name}
            </div>
            <div>{selectedSessionData.session_type}</div>
            {selectedSessionData.is_ingested && (
              <div className="text-green-600 dark:text-green-400 mt-2">✓ Data already ingested</div>
            )}
          </div>
        )}

        {/* Action Button */}
        <Button
          onClick={handleIngestAndLoad}
          disabled={!canIngest || ingesting}
          isLoading={ingesting}
          className="w-full"
        >
          {selectedSessionData?.is_ingested ? "Load Session" : "Ingest & Load"}
        </Button>
      </div>
    </Card>
  );
}
