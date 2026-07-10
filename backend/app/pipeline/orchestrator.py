"""Self-Healing Pipeline Orchestrator — the core state machine.

Implements the iterative agentic loop:
RETRIEVE -> EVALUATE -> (HEAL if needed) -> GENERATE -> VALIDATE -> RETURN
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.pipeline.retriever import Retriever
from app.pipeline.evaluator import Evaluator
from app.pipeline.healer import Healer
from app.pipeline.generator import Generator
from app.pipeline.validator import Validator

logger = logging.getLogger(__name__)


class PipelineState:
    """Mutable state container for a single pipeline run."""

    def __init__(self, query: str, top_k: int = 4, enable_web_fallback: bool = False):
        self.query_id: str = str(uuid.uuid4())
        self.query: str = query
        self.top_k: int = top_k
        self.enable_web_fallback: bool = enable_web_fallback

        self.current_query: str = query  # may be rewritten during healing
        self.retrieved_docs: list[dict] = []
        self.evaluation_result: Optional[dict] = None
        self.healing_actions: list[dict] = []
        self.healing_attempts: int = 0
        self.regeneration_attempts: int = 0
        self.generated_answer: Optional[str] = None
        self.citations: list[dict] = []
        self.validation_result: Optional[dict] = None
        self.final_answer: Optional[str] = None
        self.confidence_score: float = 0.0
        self.final_status: str = "running"
        self.pipeline_logs: list[dict] = []
        self.error_message: Optional[str] = None

    def log(self, step: str, message: str, score: Optional[float] = None, details: Optional[dict] = None):
        self.pipeline_logs.append({
            "step": step,
            "message": message,
            "score": score,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("[%s] %s (score=%s)", step, message, score)


class Orchestrator:
    """State machine that runs the self-healing pipeline loop."""

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        evaluator: Optional[Evaluator] = None,
        healer: Optional[Healer] = None,
        generator: Optional[Generator] = None,
        validator: Optional[Validator] = None,
    ):
        self.retriever = retriever or Retriever()
        self.evaluator = evaluator or Evaluator()
        self.healer = healer or Healer()
        self.generator = generator or Generator()
        self.validator = validator or Validator()

    async def run(self, query: str, top_k: int = 4, enable_web_fallback: bool = False) -> PipelineState:
        """Execute the full self-healing pipeline."""
        state = PipelineState(query, top_k, enable_web_fallback)

        try:
            # ──────────────────────────────────────────────────
            # STEP 1: RETRIEVE
            # ──────────────────────────────────────────────────
            await self._step_retrieve(state)

            # ──────────────────────────────────────────────────
            # STEP 2-3: EVALUATE -> (HEAL loop if needed)
            # ──────────────────────────────────────────────────
            await self._step_evaluate_and_heal(state)

            # ──────────────────────────────────────────────────
            # STEP 4: GENERATE
            # ──────────────────────────────────────────────────
            await self._step_generate(state)

            # ──────────────────────────────────────────────────
            # STEP 5: VALIDATE (with regeneration loop)
            # ──────────────────────────────────────────────────
            await self._step_validate(state)

            # ──────────────────────────────────────────────────
            # COMPLETE
            # ──────────────────────────────────────────────────
            state.final_status = self._determine_final_status(state)
            self._compute_confidence(state)
            state.log("complete", f"Pipeline finished with status: {state.final_status}",
                       score=state.confidence_score)

        except Exception as e:
            logger.exception("Pipeline failed unexpectedly")
            state.final_status = "failed"
            state.error_message = str(e)
            state.log("failed", f"Pipeline error: {str(e)}")

        return state

    async def _step_retrieve(self, state: PipelineState):
        """Retrieve documents from vector store."""
        state.log("retrieve", f"Retrieving documents for query (top_k={state.top_k})")

        # Use a simple embedding mock for dev (sentence-transformers would be used in prod)
        mock_embedding = [0.0] * settings.embedding_dim
        docs = await self.retriever.retrieve(
            query=state.current_query,
            embedding=mock_embedding,
            top_k=state.top_k,
        )

        state.retrieved_docs = docs
        state.log("retrieve", f"Retrieved {len(docs)} documents")

    async def _step_evaluate_and_heal(self, state: PipelineState):
        """Evaluate relevance and heal if needed (iterative loop)."""
        while state.healing_attempts < settings.max_healing_attempts:
            # EVALUATE
            eval_result = await self.evaluator.evaluate_relevance(
                state.current_query, state.retrieved_docs
            )
            state.evaluation_result = eval_result

            avg_score = eval_result.get("evaluator_score", 0.0)
            is_relevant = eval_result.get("is_relevant", False)

            state.log(
                "evaluate",
                f"Relevance evaluation: avg_score={avg_score:.3f}, threshold={settings.relevance_threshold}",
                score=avg_score,
                details={"is_relevant": is_relevant, "scores": eval_result.get("relevance_scores", [])},
            )

            if is_relevant:
                state.log("evaluate", "Relevance PASSED. Proceeding to generation.", score=avg_score)
                return

            # HEAL
            state.healing_attempts += 1
            state.log(
                "heal",
                f"Relevance FAILED (avg={avg_score:.3f} < {settings.relevance_threshold}). "
                f"Starting healing attempt #{state.healing_attempts}",
                score=avg_score,
            )

            healing_action = await self.healer.heal(
                query=state.current_query,
                scores=eval_result.get("relevance_scores", []),
                attempt=state.healing_attempts,
                current_k=state.top_k,
            )
            state.healing_actions.append(healing_action)
            state.log("heal", f"Healing action: {healing_action.get('action', 'unknown')}",
                      details=healing_action)

            # Track state changes from healing
            if healing_action.get("action") == "query_rewrite":
                state.current_query = healing_action.get("rewritten_query", state.query)
            elif healing_action.get("action") == "parameter_adjust":
                state.top_k = healing_action.get("new_top_k", state.top_k)

            # Re-retrieve with updated query/params
            await self._step_retrieve(state)

        # Max healing attempts reached
        state.log(
            "heal",
            f"Maximum healing attempts ({settings.max_healing_attempts}) exhausted. "
            "Proceeding with best available documents.",
        )

    async def _step_generate(self, state: PipelineState):
        """Generate answer from retrieved documents."""
        state.log("generate", "Generating answer from retrieved documents")

        gen_result = await self.generator.generate(
            query=state.current_query,
            documents=state.retrieved_docs,
        )

        state.generated_answer = gen_result.get("answer", "")
        state.citations = gen_result.get("citations", [])
        state.log("generate", f"Generated answer ({len(state.generated_answer)} chars)",
                  details={"citation_count": len(state.citations)})

    async def _step_validate(self, state: PipelineState):
        """Validate answer grounding with regeneration loop."""
        while state.regeneration_attempts < settings.max_regeneration_attempts:
            if not state.generated_answer:
                return

            val_result = await self.validator.validate(
                query=state.current_query,
                answer=state.generated_answer,
                documents=state.retrieved_docs,
            )
            state.validation_result = val_result

            confidence = val_result.get("confidence_score", 0.0)
            is_grounded = val_result.get("is_grounded", False)
            issues = val_result.get("issues", [])

            state.log(
                "validate",
                f"Validation: is_grounded={is_grounded}, confidence={confidence:.3f}",
                score=confidence,
                details={"issues": issues, "feedback": val_result.get("feedback", "")},
            )

            if is_grounded or confidence >= settings.generation_confidence_threshold:
                state.final_answer = state.generated_answer
                state.confidence_score = confidence
                state.log("validate", "Validation PASSED. Answer is grounded.", score=confidence)
                return
            else:
                # Regenerate with feedback
                state.regeneration_attempts += 1
                state.log(
                    "validate",
                    f"Validation FAILED. Regeneration attempt #{state.regeneration_attempts}. "
                    f"Issues: {', '.join(issues)}",
                )
                # Re-generate (the generator would ideally incorporate feedback)
                await self._step_generate(state)

        # Max regeneration attempts reached — use last answer with current confidence
        state.final_answer = state.generated_answer
        state.confidence_score = state.validation_result.get("confidence_score", 0.0) if state.validation_result else 0.0
        state.log(
            "validate",
            f"Max regeneration attempts ({settings.max_regeneration_attempts}) reached. "
            f"Using best available answer.",
        )

    def _determine_final_status(self, state: PipelineState) -> str:
        """Determine final status based on pipeline execution."""
        if state.error_message:
            return "failed"
        if state.healing_attempts > 0:
            return "healed" if state.confidence_score >= settings.generation_confidence_threshold else "degraded"
        return "success"

    def _compute_confidence(self, state: PipelineState):
        """Compute final confidence score from evaluation and validation."""
        eval_score = state.evaluation_result.get("evaluator_score", 0.0) if state.evaluation_result else 0.0
        val_score = state.validation_result.get("confidence_score", 0.0) if state.validation_result else 0.0

        # Weighted combination
        if val_score > 0 and eval_score > 0:
            state.confidence_score = round(0.3 * eval_score + 0.7 * val_score, 2)
        elif val_score > 0:
            state.confidence_score = round(val_score, 2)
        else:
            state.confidence_score = round(eval_score, 2)
