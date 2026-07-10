"""Vector database retrieval using Qdrant client."""

import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import settings

logger = logging.getLogger(__name__)


class Retriever:
    """Handles document retrieval from Qdrant vector store."""

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection = settings.qdrant_collection

    async def initialize(self):
        """Connect to Qdrant and ensure collection exists."""
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=settings.embedding_dim,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'", self.collection)

    async def retrieve(self, query: str, embedding: list[float], top_k: int = 4) -> list[dict]:
        """Retrieve top-k documents from vector store."""
        if self.client is None:
            await self.initialize()

        hits = self.client.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=top_k,
            with_payload=True,
        )

        results = []
        for hit in hits:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "content": hit.payload.get("content", ""),
                "source": hit.payload.get("source", "unknown"),
                "metadata": hit.payload.get("metadata", {}),
            })

        logger.info("Retrieved %d documents for query (top_k=%d)", len(results), top_k)
        return results

    async def ingest_document(self, content: str, embedding: list[float], source: str = "", metadata: dict = None):
        """Add a document to the vector store."""
        if self.client is None:
            await self.initialize()

        point_id = self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=hash(content) % (2**63),
                    vector=embedding,
                    payload={
                        "content": content,
                        "source": source,
                        "metadata": metadata or {},
                    },
                )
            ],
        )
        logger.info("Ingested document from source: %s", source)
        return point_id
