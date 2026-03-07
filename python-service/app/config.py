import os

# Redis URL; same instance as Go. Default for local dev.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# LLM: primary Groq, fallback Gemini (LiteLLM model strings).
LITELLM_PRIMARY_MODEL = os.getenv("LITELLM_PRIMARY_MODEL", "groq/llama-3-8b-8192")
LITELLM_FALLBACK_MODEL = os.getenv("LITELLM_FALLBACK_MODEL", "gemini/gemini-1.5-flash")
