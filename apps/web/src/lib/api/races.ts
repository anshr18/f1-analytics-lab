/**
 * F1 Intelligence Hub - Races API
 *
 * API functions for seasons and events.
 */

import { apiGet } from "./client";
import type { Season, Event, EventListResponse } from "@/types/api";

export async function fetchSeasons(): Promise<Season[]> {
  return apiGet<Season[]>("/seasons");
}

export async function fetchEvents(seasonYear?: number): Promise<Event[]> {
  const response = await apiGet<EventListResponse>("/events", {
    season_year: seasonYear,
  });
  return response.events;
}

export async function fetchEvent(eventId: string): Promise<Event> {
  return apiGet<Event>(`/events/${eventId}`);
}
