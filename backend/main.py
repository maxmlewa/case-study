from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import re
from enum import Enum
import json
from pathlib import Path
from llm_client import rewrite_markdown_with_llm

app = FastAPI(title="Instalily Case Study API")

GUIDES_DB_PATH = Path(__file__).parent / "data" / "guides_seed.json"

def load_guides_db() -> Dict[str, Dict[str, Any]]:
    items = json.loads(GUIDES_DB_PATH.read_text())
    return {g["part_number"].upper(): g for g in items}

GUIDES_DB = load_guides_db()

def format_install_guide_md(guide: Dict[str, Any]) -> str:
    tools = guide.get("tools", [])
    safety = guide.get("safety", [])
    steps = guide.get("steps", [])

    tools_md = "\n".join([f"- {t}" for t in tools]) if tools else "- (not specified)"
    safety_md = "\n".join([f"- {s}" for s in safety]) if safety else "- (not specified)"
    steps_md = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)]) if steps else "1. (not specified)"

    return (
        f"**{guide.get('title', 'Installation instructions')}**\n\n"
        f"**Tools you may need**\n{tools_md}\n\n"
        f"**Safety**\n{safety_md}\n\n"
        f"**Steps**\n{steps_md}\n"
    )


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



PARTS_DB_PATH = Path(__file__).parent / "data" / "parts_seed.json"

def load_parts_db() -> Dict[str, Dict[str, Any]]:
    items = json.loads(PARTS_DB_PATH.read_text())
    return {p["part_number"].upper(): p for p in items}

PARTS_DB = load_parts_db()

def extract_part_number(text: str) -> Optional[str]:
    m = re.search(r"\b(PS\d{5,})\b", text.upper())
    return m.group(1) if m else None

def make_product_card(part: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "product",
        "part_number": part["part_number"],
        "title": part["title"],
        "price": part["price"],
        "availability": part["availability"],
        "image_url": part["image_url"],
        "url": part["url"],
        "actions": [
            {"label": "Installation steps", "action": "INSTALL", "payload": {"part_number": part["part_number"]}},
            {"label": "Check compatibility", "action": "COMPATIBILITY", "payload": {"part_number": part["part_number"]}}
        ]
    }




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

    

    part_number = extract_part_number(user_text)
    part = PARTS_DB.get(part_number) if part_number else None
    cards = [make_product_card(part)] if part else []

    guide = GUIDES_DB.get(part_number) if part_number else None

    if intent == Intent.INSTALL:
        if part and guide:
            md = format_install_guide_md(guide)

            # Optional LLM rewrite (fallback returns None)
            rewritten = rewrite_markdown_with_llm(
                system="You are a helpful PartSelect repair assistant. Keep it concise, safe, and step-by-step.",
                user=f"User asked: {user_text}\n\nHere are the facts:\n{md}\n\nRewrite cleanly in markdown."
            )

            content = rewritten or md
            citations = guide.get("citations", [])
        elif part and not guide:
            content = (
                f"I found {part['part_number']} ({part['title']}), but I don’t have an installation guide for it yet. "
                "Share your model number and I can still outline the general replacement steps."
            )
            citations = []
        else:
            content = "What part number are you installing? (Example: PS11752778)"
            citations = []

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
        "cards": cards,
        "memory": req.context or {}
    }
