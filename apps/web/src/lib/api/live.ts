/**
 * Live Streaming API Client
 *
 * Client functions for live F1 data streaming endpoints.
 */

import { apiClient } from './client';

export interface LiveSession {
  id: string;
  session_id: string;
  is_active: boolean;
  openf1_session_key: string;
  current_lap: number | null;
  session_status: string;
  track_status: string;
  started_at?: string;
}

export interface LiveTiming {
  driver_number: number;
  lap_number: number;
  position: number;
  gap_to_leader: number | null;
  interval: number | null;
  last_lap_time: number | null;
  sector1_time: number | null;
  sector2_time: number | null;
  sector3_time: number | null;
  timestamp: string;
}

export interface LiveEvent {
  id: string;
  event_type: string;
  driver_number: number | null;
  lap_number: number | null;
  message: string;
  flag: string | null;
  data: Record<string, any>;
  timestamp: string;
}

export interface LiveUpdate {
  type: 'live_update';
  data: {
    timing: any[];
    pit_stops: any[];
    race_control: any[];
    session_status: any;
    weather: any;
  };
  timestamp: string;
  session_id: string;
}

/**
 * Start a live streaming session
 */
export async function startLiveSession(
  sessionId: string,
  openf1SessionKey: string
): Promise<LiveSession> {
  const response = await apiClient.post<LiveSession>(
    `/live/sessions/start`,
    null,
    {
      params: {
        session_id: sessionId,
        openf1_session_key: openf1SessionKey,
      },
    }
  );
  return response.data;
}

/**
 * Stop a live streaming session
 */
export async function stopLiveSession(
  liveSessionId: string
): Promise<{ message: string; live_session_id: string }> {
  const response = await apiClient.post(
    `/live/sessions/${liveSessionId}/stop`
  );
  return response.data;
}

/**
 * Get all active live sessions
 */
export async function getActiveLiveSessions(): Promise<LiveSession[]> {
  const response = await apiClient.get<LiveSession[]>('/live/sessions/active');
  return response.data;
}

/**
 * Get live timing data for a session
 */
export async function getLiveTiming(
  liveSessionId: string,
  limit: number = 100
): Promise<LiveTiming[]> {
  const response = await apiClient.get<LiveTiming[]>(
    `/live/sessions/${liveSessionId}/timing`,
    {
      params: { limit },
    }
  );
  return response.data;
}

/**
 * Get live events for a session
 */
export async function getLiveEvents(
  liveSessionId: string,
  eventType?: string,
  limit: number = 100
): Promise<LiveEvent[]> {
  const response = await apiClient.get<LiveEvent[]>(
    `/live/sessions/${liveSessionId}/events`,
    {
      params: { event_type: eventType, limit },
    }
  );
  return response.data;
}

/**
 * Get WebSocket connection count
 */
export async function getConnectionCount(
  sessionId?: string
): Promise<{ count: number; session_id: string | null }> {
  const response = await apiClient.get<{ count: number; session_id: string | null }>(
    '/live/connections/count',
    {
      params: sessionId ? { session_id: sessionId } : {},
    }
  );
  return response.data;
}
