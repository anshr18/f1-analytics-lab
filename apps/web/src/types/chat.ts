/**
 * Chat & RAG API Types
 */

export interface ChatSession {
  id: string;
  user_id: string | null;
  title: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  retrieved_chunks?: string[];
  metadata?: Record<string, any>;
}

export interface ChatSource {
  embedding_id: string;
  document_id: string;
  chunk_text: string;
  chunk_index: number;
  document_title: string;
  document_type: string;
  similarity: number;
}

export interface ChatUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatSessionCreate {
  user_id?: string;
  title?: string;
  metadata?: Record<string, any>;
}

export interface ChatMessageSend {
  message: string;
  use_rag?: boolean;
  top_k?: number;
  similarity_threshold?: number;
}

export interface ChatMessageResponse {
  message: ChatMessage;
  sources?: ChatSource[];
  usage: ChatUsage;
}

export interface ChatSessionListResponse {
  sessions: ChatSession[];
  total: number;
}

export interface ChatHistoryResponse {
  session: ChatSession;
  messages: ChatMessage[];
  total_messages: number;
}

export interface RAGQueryRequest {
  question: string;
  top_k?: number;
  similarity_threshold?: number;
  doc_type?: string;
}

export interface RAGQueryResponse {
  answer: string;
  sources: ChatSource[];
  num_sources: number;
  model: string;
  usage: ChatUsage;
}

export interface DocumentIngestRequest {
  title: string;
  content: string;
  doc_type?: string;
  source_url?: string;
  metadata?: Record<string, any>;
}

export interface DocumentResponse {
  id: string;
  doc_type: string;
  title: string;
  created_at: string;
  num_chunks: number;
}

export interface DocumentCountResponse {
  counts: Record<string, number>;
  total: number;
}

export interface BulkIngestRequest {
  limit?: number;
}

export interface BulkIngestResponse {
  documents: DocumentResponse[];
  count: number;
}
