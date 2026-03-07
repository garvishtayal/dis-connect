import os

# Redis URL; same instance as Go. Default for local dev.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# LLM: primary Groq, fallback Gemini (LiteLLM model strings; use current model IDs).
LITELLM_PRIMARY_MODEL = os.getenv("LITELLM_PRIMARY_MODEL", "groq/llama-3.1-8b-instant")
LITELLM_FALLBACK_MODEL = os.getenv("LITELLM_FALLBACK_MODEL", "gemini/gemini-2.0-flash")
