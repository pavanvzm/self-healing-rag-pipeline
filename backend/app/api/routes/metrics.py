"""API routes for dashboard metrics and query history."""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    MetricsSummary, QueryHistoryItem, DashboardData,
    TimeSeriesPoint, ConfidenceDistribution, HealingActionDistribution,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["metrics"])

# ──────────────────────────────────────────────
# Mock data store for development
# In production, this would query PostgreSQL.
# ──────────────────────────────────────────────
MOCK_QUERIES: list[dict] = [
    {
        "id": "q-001",
        "query": "What are the best practices for RAG pipeline reliability?",
        "status": "success",
        "confidence": 0.94,
        "healing_actions": 0,
        "created_at": "2026-07-09T10:30:00Z",
    },
    {
        "id": "q-002",
        "query": "How does vector search handle semantic similarity?",
        "status": "healed",
        "confidence": 0.87,
        "healing_actions": 1,
        "created_at": "2026-07-09T10:45:00Z",
    },
    {
        "id": "q-003",
        "query": "Explain transformer architecture in detail",
        "status": "success",
        "confidence": 0.91,
        "healing_actions": 0,
        "created_at": "2026-07-09T11:00:00Z",
    },
    {
        "id": "q-004",
        "query": "What is the latest research on agentic AI systems?",
        "status": "healed",
        "confidence": 0.82,
        "healing_actions": 2,
        "created_at": "2026-07-09T11:15:00Z",
    },
    {
        "id": "q-005",
        "query": "Compare PostgreSQL and MongoDB for AI applications",
        "status": "failed",
        "confidence": 0.35,
        "healing_actions": 3,
        "created_at": "2026-07-09T11:30:00Z",
    },
    {
        "id": "q-006",
        "query": "How to implement cosine similarity in Python?",
        "status": "success",
        "confidence": 0.96,
        "healing_actions": 0,
        "created_at": "2026-07-09T12:00:00Z",
    },
    {
        "id": "q-007",
        "query": "What are embeddings in natural language processing?",
        "status": "success",
        "confidence": 0.93,
        "healing_actions": 0,
        "created_at": "2026-07-09T12:30:00Z",
    },
    {
        "id": "q-008",
        "query": "Explain the attention mechanism in LLMs",
        "status": "healed",
        "confidence": 0.79,
        "healing_actions": 1,
        "created_at": "2026-07-09T13:00:00Z",
    },
    {
        "id": "q-009",
        "query": "Best practices for prompt engineering",
        "status": "success",
        "confidence": 0.95,
        "healing_actions": 0,
        "created_at": "2026-07-09T13:30:00Z",
    },
    {
        "id": "q-010",
        "query": "How does RAG reduce hallucinations in LLM outputs?",
        "status": "healed",
        "confidence": 0.88,
        "healing_actions": 1,
        "created_at": "2026-07-09T14:00:00Z",
    },
]

MOCK_LOGS: dict[str, list[dict]] = {
    "q-001": [
        {"step": "retrieve", "message": "Retrieving documents for query (top_k=4)", "score": None, "timestamp": "2026-07-09T10:30:01Z"},
        {"step": "retrieve", "message": "Retrieved 4 documents", "score": None, "timestamp": "2026-07-09T10:30:02Z"},
        {"step": "evaluate", "message": "Relevance evaluation: avg_score=0.850", "score": 0.85, "timestamp": "2026-07-09T10:30:03Z"},
        {"step": "evaluate", "message": "Relevance PASSED. Proceeding to generation.", "score": 0.85, "timestamp": "2026-07-09T10:30:03Z"},
        {"step": "generate", "message": "Generating answer from retrieved documents", "score": None, "timestamp": "2026-07-09T10:30:04Z"},
        {"step": "generate", "message": "Generated answer (425 chars)", "score": None, "timestamp": "2026-07-09T10:30:05Z"},
        {"step": "validate", "message": "Validation: is_grounded=True, confidence=0.940", "score": 0.94, "timestamp": "2026-07-09T10:30:06Z"},
        {"step": "validate", "message": "Validation PASSED. Answer is grounded.", "score": 0.94, "timestamp": "2026-07-09T10:30:06Z"},
        {"step": "complete", "message": "Pipeline finished with status: success", "score": 0.94, "timestamp": "2026-07-09T10:30:07Z"},
    ],
    "q-002": [
        {"step": "retrieve", "message": "Retrieving documents for query (top_k=4)", "score": None, "timestamp": "2026-07-09T10:45:01Z"},
        {"step": "retrieve", "message": "Retrieved 4 documents", "score": None, "timestamp": "2026-07-09T10:45:02Z"},
        {"step": "evaluate", "message": "Relevance evaluation: avg_score=0.450", "score": 0.45, "timestamp": "2026-07-09T10:45:03Z"},
        {"step": "evaluate", "message": "Relevance FAILED. Starting healing attempt #1", "score": 0.45, "timestamp": "2026-07-09T10:45:03Z"},
        {"step": "heal", "message": "Healing action: query_rewrite", "score": None, "timestamp": "2026-07-09T10:45:04Z"},
        {"step": "retrieve", "message": "Re-retrieving with rewritten query", "score": None, "timestamp": "2026-07-09T10:45:05Z"},
        {"step": "evaluate", "message": "Relevance evaluation: avg_score=0.720", "score": 0.72, "timestamp": "2026-07-09T10:45:06Z"},
        {"step": "evaluate", "message": "Relevance PASSED. Proceeding to generation.", "score": 0.72, "timestamp": "2026-07-09T10:45:06Z"},
        {"step": "generate", "message": "Generating answer", "score": None, "timestamp": "2026-07-09T10:45:07Z"},
        {"step": "validate", "message": "Validation: is_grounded=True, confidence=0.870", "score": 0.87, "timestamp": "2026-07-09T10:45:08Z"},
        {"step": "complete", "message": "Pipeline finished with status: healed", "score": 0.87, "timestamp": "2026-07-09T10:45:09Z"},
    ],
}


@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary():
    """Get aggregated pipeline metrics."""
    total = len(MOCK_QUERIES)
    if total == 0:
        return MetricsSummary(total_queries=0, avg_confidence=0, avg_healing_iterations=0,
                              error_rate=0, success_rate=0, healed_rate=0)

    avg_conf = sum(q["confidence"] for q in MOCK_QUERIES) / total
    avg_heal = sum(q["healing_actions"] for q in MOCK_QUERIES) / total
    errors = sum(1 for q in MOCK_QUERIES if q["status"] == "failed")
    success = sum(1 for q in MOCK_QUERIES if q["status"] == "success")
    healed = sum(1 for q in MOCK_QUERIES if q["status"] == "healed")

    return MetricsSummary(
        total_queries=total,
        avg_confidence=round(avg_conf, 2),
        avg_healing_iterations=round(avg_heal, 2),
        error_rate=round(errors / total * 100, 1),
        success_rate=round(success / total * 100, 1),
        healed_rate=round(healed / total * 100, 1),
    )


@router.get("/queries/history", response_model=list[QueryHistoryItem])
async def get_query_history(limit: int = 10):
    """Get recent query history."""
    recent = MOCK_QUERIES[-limit:]
    recent.reverse()
    return [QueryHistoryItem(**q) for q in recent]


@router.get("/queries/{query_id}", response_model=dict)
async def get_query_detail(query_id: str):
    """Get detailed view of a single query execution."""
    query = next((q for q in MOCK_QUERIES if q["id"] == query_id), None)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    logs = MOCK_LOGS.get(query_id, [])
    return {
        "query": query,
        "pipeline_logs": logs,
        "pipeline_steps": [
            {"step": "retrieve", "label": "Retrieve", "status": "completed"},
            {"step": "evaluate", "label": "Evaluate", "status": "completed"},
            {"step": "heal", "label": "Heal", "status": "completed" if query["healing_actions"] > 0 else "skipped"},
            {"step": "generate", "label": "Generate", "status": "completed"},
            {"step": "validate", "label": "Validate", "status": "completed"},
        ],
    }


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Get all dashboard data in one call."""
    summary = await get_metrics_summary()
    history = await get_query_history(10)

    # Time series data (mock)
    queries_over_time = [
        TimeSeriesPoint(date="2026-07-03", count=5),
        TimeSeriesPoint(date="2026-07-04", count=12),
        TimeSeriesPoint(date="2026-07-05", count=8),
        TimeSeriesPoint(date="2026-07-06", count=15),
        TimeSeriesPoint(date="2026-07-07", count=22),
        TimeSeriesPoint(date="2026-07-08", count=18),
        TimeSeriesPoint(date="2026-07-09", count=10),
    ]

    # Confidence distribution (mock)
    confidence_distribution = [
        ConfidenceDistribution(range="0-20%", count=1),
        ConfidenceDistribution(range="20-40%", count=0),
        ConfidenceDistribution(range="40-60%", count=1),
        ConfidenceDistribution(range="60-80%", count=2),
        ConfidenceDistribution(range="80-100%", count=6),
    ]

    # Healing action distribution (mock)
    healing_distribution = [
        HealingActionDistribution(action="Query Rewrite", count=4),
        HealingActionDistribution(action="Parameter Adjust", count=2),
        HealingActionDistribution(action="Web Search", count=1),
    ]

    return DashboardData(
        summary=summary,
        queries_over_time=queries_over_time,
        confidence_distribution=confidence_distribution,
        healing_distribution=healing_distribution,
        recent_queries=history,
    )
