import os
from typing import Optional

def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) # may switch to other keys or include other keys

def rewrite_markdown_with_llm(*, system: str, user: str) -> Optional[str]:
    """
    Pluggable hook:
    - If any key exists, will implement an LLM call here. - TODO
    - If not, return None and the caller will use fallback text.
    """
    if not llm_enabled():
        return None

    # Intentionally left as fallback for now.
    # TODO Add provider call later without changing agent logic.
    return None