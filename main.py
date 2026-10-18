"""
Production RAG & Agent State Backend
------------------------------------
FastAPI application handling vector search retrieval and execution state 
management for high-volume agentic pipelines.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Agent RAG & State Backend", version="1.0.0")

# In-memory mock vector store & session state DB
VECTOR_STORE = [
    {"id": "doc_1", "text": "Tether provides stablecoin liquidity infrastructure globally.", "embedding": [0.1, 0.2]},
    {"id": "doc_2", "text": "Multi-agent orchestration requires strict JSON schema contracts.", "embedding": [0.4, 0.5]}
]

SESSION_STATES = {}

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    session_id: str
    retrieved_contexts: List[str]
    status: str

@app.post("/api/v1/query", response_model=QueryResponse)
def process_agent_query(payload: QueryRequest):
    """Retrieves context via vector search and maintains agent state per session."""
    session_id = payload.session_id or str(uuid.uuid4())
    
    # Mock retrieval logic based on query keywords
    matched_docs = [doc["text"] for doc in VECTOR_STORE if any(word in doc["text"].lower() for word in payload.query.lower().split())]
    if not matched_docs:
        matched_docs = [VECTOR_STORE[0]["text"]] # Fallback default

    # Update session state history
    if session_id not in SESSION_STATES:
        SESSION_STATES[session_id] = []
    SESSION_STATES[session_id].append({"query": payload.query, "retrieved": matched_docs})

    return {
        "session_id": session_id,
        "retrieved_contexts": matched_docs,
        "status": "success"
    }

@app.get("/api/v1/state/{session_id}")
def get_session_state(session_id: str):
    """Fetches execution state history for debugging and trace diagnostics."""
    if session_id not in SESSION_STATES:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, "history": SESSION_STATES[session_id]}
