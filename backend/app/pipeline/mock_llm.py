"""Mock LLM service for local development without real API keys."""

import json
import random
from typing import Optional


class MockLLMService:
    """Simulates LLM responses for development and testing."""

    def __init__(self, model: str = "mock-model"):
        self.model = model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate a mock response based on prompt content."""
        prompt_lower = prompt.lower()

        if "grade" in prompt_lower or "relevance" in prompt_lower or "score" in prompt_lower:
            return self._mock_grade(prompt)

        if "rewrite" in prompt_lower or "improve" in prompt_lower:
            return self._mock_rewrite(prompt)

        if "validate" in prompt_lower or "grounded" in prompt_lower or "fact" in prompt_lower:
            return self._mock_validate(prompt)

        # Default generation
        return self._mock_answer(prompt)

    def _mock_grade(self, prompt: str) -> str:
        """Simulate relevance grading."""
        score = round(random.uniform(0.3, 1.0), 2)
        return json.dumps({
            "relevance_scores": [max(0.1, min(1.0, score + random.uniform(-0.2, 0.2))) for _ in range(3)],
            "average_score": score,
            "is_relevant": score >= 0.6,
            "reasoning": "Mock evaluation of document relevance."
        })

    def _mock_rewrite(self, prompt: str) -> str:
        """Simulate query rewriting."""
        return json.dumps({
            "rewritten_query": "What are the key principles and best practices for building reliable " +
                               "Retrieval-Augmented Generation systems with self-healing capabilities?",
            "expansion_terms": ["self-healing", "RAG", "reliability", "error correction"],
            "strategy": "expanded_context"
        })

    def _mock_validate(self, prompt: str) -> str:
        """Simulate answer validation."""
        score = round(random.uniform(0.5, 1.0), 2)
        return json.dumps({
            "is_grounded": score >= 0.8,
            "confidence_score": score,
            "issues": [] if score >= 0.8 else ["Answer includes unsubstantiated claims."],
            "feedback": "Answer is well-supported by sources." if score >= 0.8 else "Some claims lack direct source support."
        })

    def _mock_answer(self, prompt: str) -> str:
        """Simulate a generated answer."""
        templates = [
            "Based on the retrieved documents, the key aspects of {topic} include reliability, "
            "scalability, and maintainability. The self-healing pipeline ensures autonomous "
            "error detection and correction through iterative feedback loops.",

            "The retrieved information indicates that {topic} involves several important "
            "considerations. First, the system must implement robust evaluation mechanisms. "
            "Second, healing strategies should include query rewriting and parameter adjustment. "
            "Third, validation ensures answers remain grounded in source documents.",

            "According to the source documents, {topic} can be approached by implementing "
            "a multi-stage pipeline: retrieval, evaluation, healing (if needed), generation, "
            "and validation. This architecture provides production-grade reliability."
        ]
        template = random.choice(templates)
        # Extract a simple topic from the prompt
        words = prompt.split()[:5]
        topic = " ".join(words) if words else "this topic"
        return template.format(topic=topic)

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """Generate a structured (JSON) mock response."""
        raw = await self.generate(prompt, system_prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"result": raw}
