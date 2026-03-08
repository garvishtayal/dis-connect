from typing import Any

from litellm import completion

from app.config import LITELLM_MODELS


class LLMError(Exception):
    """Raised when all LLM models (primary + fallbacks) fail."""

    pass


# Calls LiteLLM completion for the given model and messages; returns content string or empty.
def _complete(model: str, messages: list[dict[str, str]]) -> str:
    out = completion(model=model, messages=messages)
    choice = out.choices[0] if out.choices else None
    if choice and choice.message and choice.message.content:
        return choice.message.content.strip()
    return ""


# Tries models in order (primary then fallbacks); returns first non-empty response. Raises LLMError when all fail.
def generate_text(prompt: str, **_: Any) -> str:
    messages = [{"role": "user", "content": prompt}]
    failures: list[str] = []
    for model in LITELLM_MODELS:
        try:
            out = _complete(model, messages)
            if out:
                print(f"[llm] {model}")
                return out
            failures.append(f"{model} returned empty")
        except Exception as e:
            failures.append(f"{model}: {e!s}")
    raise LLMError("; ".join(failures))


# Thin wrapper so callers can use LLMClient().generate_text(prompt).
class LLMClient:
    def __init__(self) -> None:
        pass

    # Generates text via LiteLLM (primary then fallbacks).
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return generate_text(prompt, **kwargs)
