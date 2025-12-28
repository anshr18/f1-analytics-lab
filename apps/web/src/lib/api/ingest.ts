/**
 * F1 Intelligence Hub - Ingest API
 *
 * API functions for data ingestion.
 */

import { apiGet, apiPost } from "./client";
import type { IngestSessionRequest, IngestSessionResponse, TaskStatusResponse } from "@/types/api";

export async function ingestSession(request: IngestSessionRequest): Promise<IngestSessionResponse> {
  return apiPost<IngestSessionResponse>("/ingest/session", request);
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  return apiGet<TaskStatusResponse>(`/ingest/status/${taskId}`);
}
