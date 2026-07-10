"use client";

// ──────────────────────────────────────────────
// Types
// ──────────────────────────────────────────────

export interface QueryHistoryItem {
  id: string;
  query: string;
  status: string;
  confidence: number;
  healing_actions: number;
  created_at: string;
}

export interface MetricsSummary {
  total_queries: number;
  avg_confidence: number;
  avg_healing_iterations: number;
  error_rate: number;
  success_rate: number;
  healed_rate: number;
}

export interface TimeSeriesPoint {
  date: string;
  count: number;
}

export interface ConfidenceDistribution {
  range: string;
  count: number;
}

export interface HealingActionDistribution {
  action: string;
  count: number;
}

export interface DashboardData {
  summary: MetricsSummary;
  queries_over_time: TimeSeriesPoint[];
  confidence_distribution: ConfidenceDistribution[];
  healing_distribution: HealingActionDistribution[];
  recent_queries: QueryHistoryItem[];
}

export interface PipelineLog {
  step: string;
  message: string;
  score: number | null;
  details: Record<string, unknown> | null;
  timestamp: string;
}

export interface PipelineStep {
  step: string;
  label: string;
  status: "completed" | "active" | "pending" | "skipped" | "failed";
}

export interface QueryDetail {
  query: QueryHistoryItem;
  pipeline_logs: PipelineLog[];
  pipeline_steps: PipelineStep[];
}

// ──────────────────────────────────────────────
// Mock data (frontend fallback)
// ──────────────────────────────────────────────

const MOCK_DASHBOARD: DashboardData = {
  summary: {
    total_queries: 90,
    avg_confidence: 0.84,
    avg_healing_iterations: 0.8,
    error_rate: 10,
    success_rate: 60,
    healed_rate: 30,
  },
  queries_over_time: [
    { date: "Jul 3", count: 5 },
    { date: "Jul 4", count: 12 },
    { date: "Jul 5", count: 8 },
    { date: "Jul 6", count: 15 },
    { date: "Jul 7", count: 22 },
    { date: "Jul 8", count: 18 },
    { date: "Jul 9", count: 10 },
  ],
  confidence_distribution: [
    { range: "0-20%", count: 1 },
    { range: "20-40%", count: 2 },
    { range: "40-60%", count: 4 },
    { range: "60-80%", count: 18 },
    { range: "80-100%", count: 65 },
  ],
  healing_distribution: [
    { action: "Query Rewrite", count: 24 },
    { action: "Parameter Adjust", count: 12 },
    { action: "Web Search", count: 5 },
  ],
  recent_queries: [
    { id: "q-010", query: "How does RAG reduce hallucinations in LLM outputs?", status: "healed", confidence: 0.88, healing_actions: 1, created_at: "2026-07-09T14:00:00Z" },
    { id: "q-009", query: "Best practices for prompt engineering", status: "success", confidence: 0.95, healing_actions: 0, created_at: "2026-07-09T13:30:00Z" },
    { id: "q-008", query: "Explain the attention mechanism in LLMs", status: "healed", confidence: 0.79, healing_actions: 1, created_at: "2026-07-09T13:00:00Z" },
    { id: "q-007", query: "What are embeddings in natural language processing?", status: "success", confidence: 0.93, healing_actions: 0, created_at: "2026-07-09T12:30:00Z" },
    { id: "q-006", query: "How to implement cosine similarity in Python?", status: "success", confidence: 0.96, healing_actions: 0, created_at: "2026-07-09T12:00:00Z" },
  ],
};

const MOCK_QUERY_DETAILS: Record<string, QueryDetail> = {
  "q-001": {
    query: { id: "q-001", query: "What are the best practices for RAG pipeline reliability?", status: "success", confidence: 0.94, healing_actions: 0, created_at: "2026-07-09T10:30:00Z" },
    pipeline_logs: [
      { step: "retrieve", message: "Retrieving documents for query (top_k=4)", score: null, details: null, timestamp: "2026-07-09T10:30:01Z" },
      { step: "retrieve", message: "Retrieved 4 documents", score: null, details: null, timestamp: "2026-07-09T10:30:02Z" },
      { step: "evaluate", message: "Relevance evaluation: avg_score=0.850", score: 0.85, details: null, timestamp: "2026-07-09T10:30:03Z" },
      { step: "evaluate", message: "Relevance PASSED. Proceeding to generation.", score: 0.85, details: null, timestamp: "2026-07-09T10:30:03Z" },
      { step: "generate", message: "Generating answer from retrieved documents", score: null, details: null, timestamp: "2026-07-09T10:30:04Z" },
      { step: "validate", message: "Validation: is_grounded=True, confidence=0.940", score: 0.94, details: null, timestamp: "2026-07-09T10:30:06Z" },
      { step: "validate", message: "Validation PASSED. Answer is grounded.", score: 0.94, details: null, timestamp: "2026-07-09T10:30:06Z" },
      { step: "complete", message: "Pipeline finished with status: success", score: 0.94, details: null, timestamp: "2026-07-09T10:30:07Z" },
    ],
    pipeline_steps: [
      { step: "retrieve", label: "Retrieve", status: "completed" },
      { step: "evaluate", label: "Evaluate", status: "completed" },
      { step: "heal", label: "Heal", status: "skipped" },
      { step: "generate", label: "Generate", status: "completed" },
      { step: "validate", label: "Validate", status: "completed" },
    ],
  },
  "q-002": {
    query: { id: "q-002", query: "How does vector search handle semantic similarity?", status: "healed", confidence: 0.87, healing_actions: 1, created_at: "2026-07-09T10:45:00Z" },
    pipeline_logs: [
      { step: "retrieve", message: "Retrieving documents for query (top_k=4)", score: null, details: null, timestamp: "2026-07-09T10:45:01Z" },
      { step: "retrieve", message: "Retrieved 4 documents", score: null, details: null, timestamp: "2026-07-09T10:45:02Z" },
      { step: "evaluate", message: "Relevance evaluation: avg_score=0.450", score: 0.45, details: null, timestamp: "2026-07-09T10:45:03Z" },
      { step: "evaluate", message: "Relevance FAILED. Starting healing attempt #1", score: 0.45, details: null, timestamp: "2026-07-09T10:45:03Z" },
      { step: "heal", message: "Healing action: query_rewrite", score: null, details: null, timestamp: "2026-07-09T10:45:04Z" },
      { step: "retrieve", message: "Re-retrieving with rewritten query", score: null, details: null, timestamp: "2026-07-09T10:45:05Z" },
      { step: "evaluate", message: "Relevance evaluation: avg_score=0.720", score: 0.72, details: null, timestamp: "2026-07-09T10:45:06Z" },
      { step: "evaluate", message: "Relevance PASSED. Proceeding to generation.", score: 0.72, details: null, timestamp: "2026-07-09T10:45:06Z" },
      { step: "generate", message: "Generating answer", score: null, details: null, timestamp: "2026-07-09T10:45:07Z" },
      { step: "validate", message: "Validation: is_grounded=True, confidence=0.870", score: 0.87, details: null, timestamp: "2026-07-09T10:45:08Z" },
      { step: "complete", message: "Pipeline finished with status: healed", score: 0.87, details: null, timestamp: "2026-07-09T10:45:09Z" },
    ],
    pipeline_steps: [
      { step: "retrieve", label: "Retrieve", status: "completed" },
      { step: "evaluate", label: "Evaluate", status: "completed" },
      { step: "heal", label: "Heal", status: "completed" },
      { step: "generate", label: "Generate", status: "completed" },
      { step: "validate", label: "Validate", status: "completed" },
    ],
  },
};

// ──────────────────────────────────────────────
// API Client
// ──────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export function getDashboardData(): Promise<DashboardData> {
  return fetchApi("/api/dashboard", MOCK_DASHBOARD);
}

export function getQueryDetail(id: string): Promise<QueryDetail> {
  const fallback = MOCK_QUERY_DETAILS[id] || {
    query: { id, query: "Unknown query", status: "unknown", confidence: 0, healing_actions: 0, created_at: "" },
    pipeline_logs: [],
    pipeline_steps: [],
  };
  return fetchApi(`/api/queries/${id}`, fallback);
}
