/**
 * Chat & RAG API Client
 */

import type {
  ChatSession,
  ChatSessionCreate,
  ChatSessionListResponse,
  ChatHistoryResponse,
  ChatMessageSend,
  ChatMessageResponse,
  RAGQueryRequest,
  RAGQueryResponse,
  DocumentIngestRequest,
  DocumentResponse,
  DocumentCountResponse,
  BulkIngestRequest,
  BulkIngestResponse,
} from "@/types/chat";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Create a new chat session
 */
export async function createChatSession(
  data: ChatSessionCreate = {}
): Promise<ChatSession> {
  const response = await fetch(`${API_BASE}/chat/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create chat session: ${response.statusText}`);
  }

  return response.json();
}

/**
 * List chat sessions
 */
export async function listChatSessions(params?: {
  user_id?: string;
  limit?: number;
  offset?: number;
}): Promise<ChatSessionListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.user_id) searchParams.set("user_id", params.user_id);
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());

  const url = `${API_BASE}/chat/sessions${
    searchParams.toString() ? `?${searchParams.toString()}` : ""
  }`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to list chat sessions: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get chat session history
 */
export async function getChatSessionHistory(
  sessionId: string,
  limit?: number
): Promise<ChatHistoryResponse> {
  const searchParams = new URLSearchParams();
  if (limit) searchParams.set("limit", limit.toString());

  const url = `${API_BASE}/chat/sessions/${sessionId}${
    searchParams.toString() ? `?${searchParams.toString()}` : ""
  }`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get chat history: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Send a message in a chat session
 */
export async function sendChatMessage(
  sessionId: string,
  data: ChatMessageSend
): Promise<ChatMessageResponse> {
  const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Delete a chat session
 */
export async function deleteChatSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Failed to delete chat session: ${response.statusText}`);
  }
}

/**
 * Execute a one-off RAG query without a session
 */
export async function executeRAGQuery(
  data: RAGQueryRequest
): Promise<RAGQueryResponse> {
  const response = await fetch(`${API_BASE}/chat/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to execute RAG query: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Ingest a custom document
 */
export async function ingestDocument(
  data: DocumentIngestRequest
): Promise<DocumentResponse> {
  const response = await fetch(`${API_BASE}/chat/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to ingest document: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get document counts by type
 */
export async function getDocumentCounts(): Promise<DocumentCountResponse> {
  const response = await fetch(`${API_BASE}/chat/documents/count`);

  if (!response.ok) {
    throw new Error(`Failed to get document counts: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Bulk ingest F1 sessions as documents
 */
export async function bulkIngestSessions(
  data: BulkIngestRequest = {}
): Promise<BulkIngestResponse> {
  const response = await fetch(`${API_BASE}/chat/documents/bulk-ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to bulk ingest sessions: ${response.statusText}`);
  }

  return response.json();
}
