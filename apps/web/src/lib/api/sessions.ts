/**
 * F1 Intelligence Hub - Sessions API
 *
 * API functions for sessions.
 */

import { apiGet } from "./client";
import type { Session, SessionListResponse } from "@/types/api";

export async function fetchSessions(eventId?: string, isIngested?: boolean): Promise<Session[]> {
  const response = await apiGet<SessionListResponse>("/sessions", {
    event_id: eventId,
    is_ingested: isIngested,
  });
  return response.sessions;
}

export async function fetchSession(sessionId: string): Promise<Session> {
  return apiGet<Session>(`/sessions/${sessionId}`);
}
