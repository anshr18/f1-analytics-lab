/**
 * F1 Intelligence Hub - TypeScript Types
 *
 * Type definitions for API responses.
 */

// Common types
export interface TimestampFields {
  created_at: string;
  updated_at: string;
}

// Season
export interface Season {
  year: number;
  event_count?: number;
}

// Event
export interface Event extends TimestampFields {
  id: string;
  season_year: number;
  round_number: number;
  event_name: string;
  country: string;
  location: string;
  event_date: string;
  session_count?: number;
}

export interface EventListResponse {
  total: number;
  events: Event[];
}

// Session
export interface Session extends TimestampFields {
  location: string;
  id: string;
  event_id: string;
  session_type: string;
  session_date: string;
  is_ingested: boolean;
  source?: string;
  lap_count?: number;
  stint_count?: number;
}

export interface SessionListResponse {
  total: number;
  sessions: Session[];
}

// Driver
export interface Driver extends TimestampFields {
  driver_id: string;
  full_name: string;
  abbreviation: string;
  number?: number;
  country?: string;
}

export interface DriverListResponse {
  total: number;
  drivers: Driver[];
}

// Lap
export interface Lap extends TimestampFields {
  id: string;
  session_id: string;
  driver_id: string;
  lap_number: number;
  lap_time?: string; // Timedelta as ISO duration string
  sector_1_time?: string;
  sector_2_time?: string;
  sector_3_time?: string;
  compound?: string;
  tyre_life?: number;
  stint_id?: string;
  track_status?: string;
  is_personal_best?: boolean;
  position?: number;
  deleted?: boolean;
  is_pit_out_lap?: boolean;
  is_pit_in_lap?: boolean;
  telemetry?: Record<string, any>;
}

export interface LapListResponse {
  total: number;
  laps: Lap[];
}

// Stint
export interface Stint extends TimestampFields {
  id: string;
  session_id: string;
  driver_id: string;
  stint_number: number;
  compound: string;
  lap_start: number;
  lap_end?: number;
  total_laps?: number;
}

export interface StintListResponse {
  total: number;
  stints: Stint[];
}

// Ingestion
export interface IngestSessionRequest {
  year: number;
  round_number: number;
  session_type: string;
  source?: string;
}

export interface IngestSessionResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  progress?: number;
  current?: string;
  result?: Record<string, any>;
  error?: string;
  session_id?: string;
}

// Chart data types
export interface LapChartData {
  lap_number: number;
  lap_time_seconds: number;
  driver_id: string;
  driver_name: string;
  compound?: string;
}

export interface StintChartData {
  driver_id: string;
  driver_name: string;
  stint_number: number;
  lap_start: number;
  lap_end: number;
  compound: string;
  total_laps: number;
}
