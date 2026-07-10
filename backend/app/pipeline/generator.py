"""RAG generation that produces answers with source citations."""

import logging
from typing import Optional
from app.pipeline.mock_llm import MockLLMService

logger = logging.getLogger(__name__)

GENERATION_PROMPT = """You are a precise RAG assistant. Answer the user's query using ONLY the provided context.
Cite each claim with the corresponding source number [1], [2], etc.

Context:
{context}

User Query: {query}

Instructions:
- Base your answer solely on the context above.
- Use inline citations like [1], [2] for each factual claim.
- If the context doesn't contain enough information, say so.
- Be concise but thorough.
"""


class Generator:
    """Generates answers grounded in retrieved documents with citations."""

    def __init__(self, llm_service: Optional[MockLLMService] = None):
        self.llm = llm_service or MockLLMService()

    async def generate(self, query: str, documents: list[dict]) -> dict:
        """
        Generate an answer with citations from retrieved documents.
        Returns answer text and citation mapping.
        """
        # Build context string with source markers
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("source", f"source_{i}")
            context_parts.append(f"[{i}] Source: {source}\n{content}")

        context = "\n\n".join(context_parts)
        prompt = GENERATION_PROMPT.format(context=context, query=query)

        answer = await self.llm.generate(prompt, temperature=0.3)

        # Build citations from retrieved documents
        citations = []
        for i, doc in enumerate(documents, 1):
            citations.append({
                "source": doc.get("source", f"source_{i}"),
                "relevance_score": doc.get("score", 0),
                "snippet": doc.get("content", "")[:200],
            })

        logger.info("Generated answer of length %d with %d citations", len(answer), len(citations))

        return {
            "answer": answer,
            "citations": citations,
            "source_count": len(documents),
        }
