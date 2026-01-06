import os
from google import genai


# used for the fall back
def detect_appliance_type(text: str) -> str:
    t = (text or "").lower()
    if "dishwasher" in t or "dish washer" in t:
        return "dishwasher"
    if "refrigerator" in t or "fridge" in t or "freezer" in t:
        return "refrigerator"
    return "appliance"


_client = None

def gemini_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

def _client_instance():
    global _client
    if _client is None:
        _client = genai.Client()
    return _client

def gemini_rewrite(grounded_text: str) -> str:
    if not gemini_enabled():
        return grounded_text

    try:
        client = _client_instance()
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                "Rewrite the following support response for clarity and friendliness. "
                "Do NOT add new facts, part numbers, prices, or compatibility claims. "
                "Keep safety steps and all numbered/bulleted steps intact. Output Markdown.\n\n"
                + grounded_text
            ),
        )
        return (resp.text or grounded_text).strip()
    except Exception:
        return grounded_text

def gemini_fallback(user_text: str) -> str:
    if not gemini_enabled():
        return (
            "I can help with PartSelect refrigerator and dishwasher parts only. "
            "What's your appliance model number (from the sticker/door frame) and what symptom are you seeing?"
        )

    try:
        client = _client_instance()
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                "You are a PartSelect support agent LIMITED to refrigerator and dishwasher parts.\n\n"
                "Task: Ask EXACTLY ONE clarifying question that helps you proceed in determining whether it is an installation, compatibility, troubleshoot, finding part or order support.\n\n"
                "Rules:\n"
                "- Output ONE sentence ending with a question mark.\n"
                "- If the user already mentioned 'dishwasher' or 'refrigerator/fridge', DO NOT ask which appliance type it is.\n"
                "- If the user mentions a symptom (noise/leak/not draining/not cooling/no ice), ask for the MODEL NUMBER for that appliance (dishwasher or refrigerator).\n"
                "- If useful, include ONE extra detail in the same question (e.g., 'during wash or drain?'), but keep it one sentence.\n"
                "- Do NOT invent part numbers, prices, availability, or compatibility.\n\n"
                f"User: {user_text}\n"
                "Assistant:"
            ),
        )

        txt = (resp.text or "").strip()
        return txt or (
            "What's your appliance model number (from the sticker/door frame)?"
        )
    except Exception:
        return (
            "What's your appliance model number (from the sticker/door frame)?"
        )
