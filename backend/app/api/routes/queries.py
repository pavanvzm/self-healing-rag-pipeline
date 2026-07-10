"""API routes for query execution."""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, PipelineLogEntry
from app.pipeline.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["queries"])

orchestrator = Orchestrator()


@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute the self-healing RAG pipeline for a user query.
    Returns the final answer with pipeline logs and metrics.
    """
    logger.info("Received query: %s (top_k=%d, web_fallback=%s)",
                request.query[:100], request.top_k, request.enable_web_fallback)

    try:
        state = await orchestrator.run(
            query=request.query,
            top_k=request.top_k,
            enable_web_fallback=request.enable_web_fallback,
        )
    except Exception as e:
        logger.exception("Pipeline execution failed")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

    # Map state to response
    pipeline_logs = [
        PipelineLogEntry(
            step=log["step"],
            message=log["message"],
            score=log.get("score"),
            details=log.get("details"),
            timestamp=log["timestamp"],
        )
        for log in state.pipeline_logs
    ]

    response = QueryResponse(
        query_id=state.query_id,
        answer=state.final_answer or "No answer could be generated.",
        confidence_score=state.confidence_score,
        citations=state.citations,
        healing_actions=state.healing_actions,
        pipeline_logs=pipeline_logs,
        final_status=state.final_status,
    )

    logger.info("Query %s completed with status=%s confidence=%.3f",
                state.query_id, state.final_status, state.confidence_score)

    return response
