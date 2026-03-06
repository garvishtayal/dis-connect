from typing import Any


# Simple placeholder LLM client used by agent endpoints.
class LLMClient:
    def __init__(self) -> None:
        self._config: dict[str, Any] = {}

    # Generates a placeholder LLM response for the given prompt.
    def generate_text(self, prompt: str, **_: Any) -> str:
        return f"LLM placeholder response for: {prompt[:80]}"

