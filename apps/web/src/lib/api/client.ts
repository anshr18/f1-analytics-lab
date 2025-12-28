/**
 * F1 Intelligence Hub - API Client
 *
 * Base HTTP client for communicating with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Make a GET request to the API.
 */
export async function apiGet<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

/**
 * Make a POST request to the API.
 */
export async function apiPost<T>(endpoint: string, data?: any): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

/**
 * Convert ISO duration string to seconds.
 * Example: "PT1M23.456S" -> 83.456
 */
export function durationToSeconds(duration: string | null | undefined): number | null {
  if (!duration) return null;

  try {
    // Handle timedelta format from FastAPI (HH:MM:SS or seconds)
    if (duration.includes(":")) {
      const parts = duration.split(":");
      const hours = parseFloat(parts[0] || "0");
      const minutes = parseFloat(parts[1] || "0");
      const seconds = parseFloat(parts[2] || "0");
      return hours * 3600 + minutes * 60 + seconds;
    }

    // Handle ISO 8601 duration format (PT...S)
    const match = duration.match(/PT(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?/);
    if (match) {
      const minutes = parseInt(match[1] || "0", 10);
      const seconds = parseFloat(match[2] || "0");
      return minutes * 60 + seconds;
    }

    // Fallback: try to parse as float
    return parseFloat(duration);
  } catch {
    return null;
  }
}

/**
 * Format seconds to MM:SS.mmm
 */
export function formatLapTime(seconds: number | null): string {
  if (seconds === null || isNaN(seconds)) return "-";

  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toFixed(3).padStart(6, "0")}`;
}
