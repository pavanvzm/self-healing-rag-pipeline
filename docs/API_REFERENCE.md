# API Reference

## Base URL

- **Production**: `http://localhost/api`
- **Development**: `http://localhost:8000`

---

## Endpoints

### `POST /api/query`

Execute a query through the self-healing pipeline.

**Request Body:**
```json
{
  "query": "What are embeddings in NLP?",
  "top_k": 4,
  "enable_web_fallback": false
}
```

**Response:**
```json
{
  "query_id": "uuid-string",
  "answer": "Generated answer with [1] citations...",
  "confidence_score": 0.94,
  "citations": [
    {
      "source": "document_1",
      "relevance_score": 0.95,
      "snippet": "Document content preview..."
    }
  ],
  "healing_actions": [],
  "pipeline_logs": [
    {
      "step": "retrieve",
      "message": "Retrieved 4 documents",
      "score": null,
      "timestamp": "2026-07-09T10:30:01Z"
    }
  ],
  "final_status": "success"
}
```

---

### `GET /api/dashboard`

Get all dashboard metrics at once.

**Response:** See `DashboardData` schema for full structure.

---

### `GET /api/metrics/summary`

Get aggregated pipeline metrics.

---

### `GET /api/queries/history?limit=10`

Get recent query history.

---

### `GET /api/queries/{query_id}`

Get detailed execution view for a single query.

---

### `GET /health`

Health check endpoint.
