"""Post-generation validation to ensure answers are grounded in sources."""

import json
import logging
from typing import Optional
from app.config import settings
from app.pipeline.mock_llm import MockLLMService

logger = logging.getLogger(__name__)

VALIDATION_PROMPT = """You are a strict fact-checking validator for a RAG system.
Determine if the generated answer is fully grounded in the provided source documents.

Source Documents:
{context}

Generated Answer:
{answer}

Check each claim in the answer against the source documents. Identify any:
1. Claims not supported by any source
2. Numbers or statistics not present in sources
3. Hallucinated entities or concepts

Return JSON:
{{
    "is_grounded": true,
    "confidence_score": 0.92,
    "issues": [],
    "feedback": "Answer is fully supported by sources."
}}

If issues are found:
{{
    "is_grounded": false,
    "confidence_score": 0.65,
    "issues": ["Claim about X not found in sources."],
    "feedback": "Some claims lack direct source support."
}}
"""


class Validator:
    """Post-generation validator that checks answer grounding."""

    def __init__(self, llm_service: Optional[MockLLMService] = None):
        self.llm = llm_service or MockLLMService()

    async def validate(self, query: str, answer: str, documents: list[dict]) -> dict:
        """
        Validate that the generated answer is grounded in source documents.
        Returns validation result with confidence score.
        """
        # Build context
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[{i}] {doc.get('content', '')}")
        context = "\n\n".join(context_parts)

        prompt = VALIDATION_PROMPT.format(
            context=context,
            answer=answer,
        )

        try:
            raw = await self.llm.generate(prompt, temperature=0.1)
            result = json.loads(raw)

            confidence = result.get("confidence_score", 0.0)
            is_grounded = result.get("is_grounded", False)
            logger.info(
                "Validation result: is_grounded=%s, confidence=%.3f, issues=%d",
                is_grounded, confidence, len(result.get("issues", [])),
            )

            return {
                "is_grounded": is_grounded,
                "confidence_score": confidence,
                "issues": result.get("issues", []),
                "feedback": result.get("feedback", ""),
            }

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Validation parse failed: %s. Using fallback confidence.", e)
            return {
                "is_grounded": True,
                "confidence_score": settings.generation_confidence_threshold,
                "issues": [],
                "feedback": "Fallback: validation could not be parsed.",
            }
