"""Pydantic schemas for API request/response payloads."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    top_k: int = Field(default=4, ge=1, le=20)
    enable_web_fallback: bool = False


class PipelineStep(str, Enum):
    RETRIEVE = "retrieve"
    EVALUATE = "evaluate"
    HEAL = "heal"
    GENERATE = "generate"
    VALIDATE = "validate"
    COMPLETE = "complete"
    FAILED = "failed"


class HealingAction(str, Enum):
    QUERY_REWRITE = "query_rewrite"
    PARAMETER_ADJUST = "parameter_adjust"
    WEB_SEARCH = "web_search"


class PipelineLogEntry(BaseModel):
    step: PipelineStep
    message: str
    score: Optional[float] = None
    details: Optional[dict] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Citation(BaseModel):
    source: str
    relevance_score: float
    snippet: str


class QueryResponse(BaseModel):
    query_id: str
    answer: str
    confidence_score: float
    citations: list[Citation] = []
    healing_actions: list[dict] = []
    pipeline_logs: list[PipelineLogEntry] = []
    final_status: str  # success / healed / failed


class MetricsSummary(BaseModel):
    total_queries: int
    avg_confidence: float
    avg_healing_iterations: float
    error_rate: float
    success_rate: float
    healed_rate: float


class QueryHistoryItem(BaseModel):
    id: str
    query: str
    status: str
    confidence: float
    healing_actions: int
    created_at: str


class ConfidenceDistribution(BaseModel):
    range: str
    count: int


class HealingActionDistribution(BaseModel):
    action: str
    count: int


class TimeSeriesPoint(BaseModel):
    date: str
    count: int


class DashboardData(BaseModel):
    summary: MetricsSummary
    queries_over_time: list[TimeSeriesPoint]
    confidence_distribution: list[ConfidenceDistribution]
    healing_distribution: list[HealingActionDistribution]
    recent_queries: list[QueryHistoryItem]
