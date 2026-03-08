import os

# Redis URL; same instance as Go. Default for local dev.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# LLM: primary then fallbacks in order (LiteLLM model strings).
LITELLM_PRIMARY_MODEL = os.getenv("LITELLM_PRIMARY_MODEL", "groq/llama-3.1-8b-instant")
LITELLM_FALLBACK_MODEL_1 = os.getenv("LITELLM_FALLBACK_MODEL_1", "")
LITELLM_FALLBACK_MODEL_2 = os.getenv("LITELLM_FALLBACK_MODEL_2", "")
LITELLM_MODELS = [LITELLM_PRIMARY_MODEL] + [m for m in (LITELLM_FALLBACK_MODEL_1, LITELLM_FALLBACK_MODEL_2) if m]
