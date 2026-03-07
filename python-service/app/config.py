import os

# Redis URL; same instance as Go. Default for local dev.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
