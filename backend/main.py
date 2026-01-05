from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

app = FastAPI(title="Instalily Case Study API")

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    # Baseline: echo to be replaced by the agent loop
    return {
        "session_id": req.session_id,
        "messages": [
            {"role": "assistant", "content": f"You said: {req.message}", "citations": []}
        ],
        "cards": [],
        "memory": req.context or {}
    }
