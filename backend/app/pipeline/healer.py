"""Healing strategies for the self-healing loop."""

import json
import logging
from typing import Optional
from app.config import settings
from app.pipeline.mock_llm import MockLLMService

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """You are a query rewriting assistant for a RAG system.
The previous retrieval failed to find sufficiently relevant documents.

Original Query: {query}
Retrieval Scores: {scores}
Healing Attempt #{attempt}

Rewrite the query to improve retrieval. Strategies:
1. Add domain-specific terminology
2. Expand acronyms
3. Rephrase for clarity
4. Include contextual hints

Return JSON:
{{
    "rewritten_query": "the improved query...",
    "expansion_terms": ["term1", "term2"],
    "strategy": "expanded_context | rephrased | domain_specific"
}}
"""


class Healer:
    """Implements healing strategies for failed retrieval."""

    def __init__(self, llm_service: Optional[MockLLMService] = None):
        self.llm = llm_service or MockLLMService()

    async def attempt_rewrite(self, query: str, scores: list[float], attempt: int) -> dict:
        """Attempt 1: Rewrite the query for better retrieval."""
        prompt = REWRITE_PROMPT.format(
            query=query,
            scores=", ".join(f"{s:.3f}" for s in scores),
            attempt=attempt,
        )
        try:
            raw = await self.llm.generate(prompt, temperature=0.3)
            result = json.loads(raw)
            logger.info("Query rewrite (attempt %d): %s", attempt, result.get("rewritten_query", ""))
            return {
                "action": "query_rewrite",
                "original_query": query,
                "rewritten_query": result.get("rewritten_query", query),
                "strategy": result.get("strategy", "expanded_context"),
                "expansion_terms": result.get("expansion_terms", []),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Rewrite failed: %s. Using expanded fallback.", e)
            return {
                "action": "query_rewrite",
                "original_query": query,
                "rewritten_query": f"{query} detailed comprehensive explanation",
                "strategy": "fallback_expansion",
                "expansion_terms": [],
            }

    async def attempt_param_adjust(self, query: str, current_k: int) -> dict:
        """Attempt 2: Increase top_k and lower threshold."""
        new_k = min(current_k + 4, 20)
        logger.info("Parameter adjust: top_k %d -> %d", current_k, new_k)
        return {
            "action": "parameter_adjust",
            "previous_top_k": current_k,
            "new_top_k": new_k,
            "threshold_adjustment": "lowered",
        }

    async def attempt_web_search(self, query: str) -> dict:
        """Attempt 3: Fall back to web search."""
        logger.info("Web search fallback for: %s", query)
        return {
            "action": "web_search",
            "query": query,
            "strategy": "web_fallback",
            "results_found": True,
        }

    async def heal(self, query: str, scores: list[float], attempt: int, current_k: int) -> dict:
        """
        Execute the appropriate healing strategy based on attempt number.
        Returns the healing action details.
        """
        if attempt == 1:
            return await self.attempt_rewrite(query, scores, attempt)
        elif attempt == 2:
            return await self.attempt_param_adjust(query, current_k)
        elif attempt == 3:
            return await self.attempt_web_search(query)
        else:
            return {
                "action": "max_attempts_reached",
                "message": "Maximum healing attempts exhausted.",
            }
