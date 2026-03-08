from typing import Any

from litellm import completion

from app.config import LITELLM_FALLBACK_MODEL, LITELLM_PRIMARY_MODEL


# Calls LiteLLM completion for the given model and messages; returns content string.
def _complete(model: str, messages: list[dict[str, str]]) -> str:
    out = completion(model=model, messages=messages)
    choice = out.choices[0] if out.choices else None
    if choice and choice.message and choice.message.content:
        return choice.message.content.strip()
    return ""


# Tries primary model then fallback; returns LLM response or empty string on failure.
def generate_text(prompt: str, **_: Any) -> str:
    messages = [{"role": "user", "content": prompt}]
    try:
        out = _complete(LITELLM_PRIMARY_MODEL, messages)
        print(f"[llm] {LITELLM_PRIMARY_MODEL}")
        return out
    except Exception:
        try:
            out = _complete(LITELLM_FALLBACK_MODEL, messages)
            print(f"[llm] fallback {LITELLM_FALLBACK_MODEL}")
            return out
        except Exception:
            return ""


# Thin wrapper so callers can use LLMClient().generate_text(prompt).
class LLMClient:
    def __init__(self) -> None:
        pass

    # Generates text via LiteLLM (primary then fallback).
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return generate_text(prompt, **kwargs)
