from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import re

app = FastAPI(title="Instalily Case Study API")

# Scope Guard  version 2 - greeting support
GREETING_WORDS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
FRIDGE_WORDS = {"fridge", "refrigerator", "freezer", "ice maker", "icemaker"}
DISH_WORDS = {"dishwasher", "dish washer"}

IN_SCOPE_WELCOME = (
    "Hi! I can help with PartSelect refrigerator and dishwasher parts, "
    "finding parts, checking compatibility, installation steps, troubleshooting, and order support. "
    "What’s your appliance model number (e.g., WDT780SAEM1) or part number (e.g., PS11752778)?"
)

OUT_OF_SCOPE_MSG = (
    "I can help with PartSelect refrigerator and dishwasher parts only, "
    "finding parts, checking compatibility, installation steps, troubleshooting, and order support. "
    "Tell me your appliance model number (e.g., WDT780SAEM1) or part number (e.g., PS11752778)."
)

def is_greeting(text: str) -> bool:
    t = text.lower().strip()
    # handle short greetings and common phrases
    return t in GREETING_WORDS or any(t.startswith(w) for w in GREETING_WORDS)

def is_in_scope(text: str) -> bool:
    t = text.lower()

    # Explicit appliance mentions
    if any(w in t for w in FRIDGE_WORDS) or any(w in t for w in DISH_WORDS):
        return True

    # PartSelect-style part number like PS11752778
    if re.search(r"\bps\d{5,}\b", t):
        return True

    # Model-like codes combined with relevant intent words
    if re.search(r"\b[A-Z0-9]{6,}\b", text) and any(k in t for k in ["model", "compatible", "install", "part"]):
        return True

    return False


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    user_text = (req.message or "").strip()

    # Greetings
    if is_greeting(user_text):
        return {
            "session_id": req.session_id,
            "messages": [{"role": "assistant", "content": IN_SCOPE_WELCOME, "citations": []}],
            "cards": [],
            "memory": req.context or {}
        }

    # Scope guard
    if not is_in_scope(user_text):
        return {
            "session_id": req.session_id,
            "messages": [
                {"role": "assistant", "content": OUT_OF_SCOPE_MSG, "citations": []}
            ],
            "cards": [],
            "memory": req.context or {}
        }

    # echo only for in-scope requests
    return {
        "session_id": req.session_id,
        "messages": [
            {"role": "assistant", "content": f"You said: {req.message}", "citations": []}
        ],
        "cards": [],
        "memory": req.context or {}
    }
