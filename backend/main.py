from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import re
from enum import Enum

app = FastAPI(title="Instalily Case Study API")


# intent and router helpers
class Intent(str, Enum):
    INSTALL = "install"
    COMPATIBILITY = "compatibility"
    TROUBLESHOOT = "troubleshoot"
    FIND_PART = "find_part"
    ORDER_SUPPORT = "order_support"
    OTHER_IN_SCOPE = "other_in_scope"

def detect_intent(text: str) -> Intent:
    t = text.lower()

    # Order and support type language
    if any(k in t for k in ["order", "refund", "return", "cancel", "shipping", "delivery", "tracking"]):
        return Intent.ORDER_SUPPORT

    # Compatibility language
    if any(k in t for k in ["compatible", "fit", "fits", "will this work", "works with", "model"]):
        return Intent.COMPATIBILITY

    # Installation language
    if any(k in t for k in ["install", "installation", "replace", "replacement", "how do i change", "remove"]):
        return Intent.INSTALL

    # Troubleshooting language
    if any(k in t for k in [
        "not working", "won't", "doesn't", "leaking", "leak", "noisy", "noise", "error code",
        "not draining", "not cooling", "no ice", "ice maker", "icemaker"
    ]):
        return Intent.TROUBLESHOOT

    # Otherwise most likely looking for a part
    if any(k in t for k in ["part", "ps", "price", "in stock", "availability", "looking for", "need a"]):
        return Intent.FIND_PART

    return Intent.OTHER_IN_SCOPE


# Scope Guard  version 2 - greeting support
GREETING_WORDS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
FRIDGE_WORDS = {"fridge", "refrigerator", "freezer", "ice maker", "icemaker"}
DISH_WORDS = {"dishwasher", "dish washer"}

IN_SCOPE_WELCOME = (
    "Hi! I can help with PartSelect refrigerator and dishwasher parts, "
    "finding parts, checking compatibility, installation steps, troubleshooting, and order support. "
    "What's your appliance model number (e.g., WDT780SAEM1) or part number (e.g., PS11752778)?"
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
    intent = detect_intent(user_text)

    if intent == Intent.INSTALL:
        content = (
            "Got it — you are asking about installation. "
            "If you share the part number (e.g., PS11752778) and your model number, "
            "I will return the step-by-step instructions and tools needed."
        )
    elif intent == Intent.COMPATIBILITY:
        content = (
            "Got it — you are asking about compatibility. "
            "Tell me the model number (e.g., WDT780SAEM1) and the part number (PSxxxx) "
            "and I will confirm the fit."
        )
    elif intent == Intent.TROUBLESHOOT:
        content = (
            "Got it — you are troubleshooting. "
            "Tell me: (1) fridge or dishwasher, (2) brand, (3) model number if you have it, "
            "and what symptom you are seeing. I will suggest checks and likely parts."
        )
    elif intent == Intent.FIND_PART:
        content = (
            "Got it — you are looking for a part. "
            "What is your appliance type (refrigerator/dishwasher) and model number? "
            "If you already have a part number (PSxxxx), share it."
        )
    elif intent == Intent.ORDER_SUPPORT:
        content = (
            "Got it — order support. "
            "If you can share your order number (or the email used), "
            "tell me what you need help with (tracking/return/refund/cancellation)."
        )
    else:
        content = (
            "I can help with refrigerator/dishwasher parts on PartSelect. "
            "Tell me your model number or the part number you are looking at."
        )

    return {
        "session_id": req.session_id,
        "messages": [{"role": "assistant", "content": content, "citations": []}],
        "cards": [],
        "memory": req.context or {}
    }
