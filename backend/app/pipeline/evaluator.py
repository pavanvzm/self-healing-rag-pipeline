"""LLM-as-a-Judge evaluator for grading document relevance."""

import json
import logging
from typing import Optional
from app.config import settings
from app.pipeline.mock_llm import MockLLMService

logger = logging.getLogger(__name__)

RELEVANCE_JUDGE_PROMPT = """You are a strict relevance judge for a RAG system.
Evaluate how relevant each retrieved document chunk is to the user's query.

Query: {query}

Documents:
{documents}

For each document, provide:
1. A relevance score between 0.0 and 1.0
2. Brief reasoning

Return JSON format:
{{
    "relevance_scores": [0.95, 0.45, ...],
    "average_score": 0.70,
    "is_relevant": true,
    "reasoning": "Overall assessment of retrieval quality."
}}
"""


class Evaluator:
    """LLM-as-a-Judge: grades retrieved document relevance."""

    def __init__(self, llm_service: Optional[MockLLMService] = None):
        self.llm = llm_service or MockLLMService()

    async def evaluate_relevance(
        self, query: str, documents: list[dict]
    ) -> dict:
        """
        Grade retrieved documents for relevance.
        Returns dict with scores, average, and pass/fail decision.
        """
        # Build document strings
        doc_texts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")[:500]
            doc_texts.append(f"[{i}] Score: {doc.get('score', 0):.3f}\n{content}")

        prompt = RELEVANCE_JUDGE_PROMPT.format(
            query=query,
            documents="\n---\n".join(doc_texts),
        )

        try:
            raw = await self.llm.generate(prompt, temperature=0.1)
            result = json.loads(raw)

            scores = result.get("relevance_scores", [])
            avg_score = result.get("average_score", sum(scores) / len(scores) if scores else 0)
            is_relevant = avg_score >= settings.relevance_threshold

            logger.info(
                "Relevance evaluation: avg_score=%.3f, is_relevant=%s, reasoning=%s",
                avg_score, is_relevant, result.get("reasoning", ""),
            )

            return {
                "evaluator_score": avg_score,
                "is_relevant": is_relevant,
                "relevance_scores": scores,
                "reasoning": result.get("reasoning", ""),
                "raw_llm_output": raw,
            }

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to parse LLM judge output: %s. Using fallback.", e)
            # Fallback: use the vector similarity scores
            scores = [d.get("score", 0) for d in documents]
            avg = sum(scores) / len(scores) if scores else 0
            return {
                "evaluator_score": avg,
                "is_relevant": avg >= settings.relevance_threshold,
                "relevance_scores": scores,
                "reasoning": "Fallback: used vector similarity scores.",
                "raw_llm_output": str(e),
            }
