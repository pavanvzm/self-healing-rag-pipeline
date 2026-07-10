"""SQLAlchemy ORM models for persisting pipeline runs and metrics."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, Boolean
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class QueryRecord(Base):
    __tablename__ = "queries"

    id = Column(String, primary_key=True, default=_uuid)
    query_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    final_status = Column(String, default="pending")  # pending | success | healed | failed
    healing_iterations = Column(Integer, default=0)
    regeneration_iterations = Column(Integer, default=0)
    pipeline_logs = Column(JSON, default=list)
    citations = Column(JSON, default=list)
    healing_actions = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)
    source = Column(String, nullable=True)
    embedding_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class PipelineMetrics(Base):
    """Aggregated metrics snapshots for dashboard."""

    __tablename__ = "pipeline_metrics"

    id = Column(String, primary_key=True, default=_uuid)
    total_queries = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    avg_healing_iterations = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    healed_count = Column(Integer, default=0)
    snapshot_date = Column(DateTime(timezone=True), default=_now)
