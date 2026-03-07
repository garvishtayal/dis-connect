import os

# Redis URL; same instance as Go. Default for local dev.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# LLM: primary and fallback model strings for LiteLLM (e.g. openai/gpt-4o-mini, groq/llama-3).
LITELLM_PRIMARY_MODEL = os.getenv("LITELLM_PRIMARY_MODEL", "openai/gpt-4o-mini")
LITELLM_FALLBACK_MODEL = os.getenv("LITELLM_FALLBACK_MODEL", "groq/llama-3-8b-8192")
