# dis-connect Python Service

This service is the **agent / content engine** used by the Go API.  
It exposes **3 agent endpoints** that the Go service calls:

- **Understand soul**: derive soul from the user's initial prompt
- **Generate content**: return content items (query + scrape + mix + rank internally)
- **Chat**: LLM reply and `needs_new_content` flag

The service is built with **FastAPI** and is intentionally simple and modular.

---

## Folder structure

```text
python-service/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── config.py
│   ├── llm/
│   │   ├── client.py
│   │   ├── context_builder.py
│   │   └── prompts.py
│   ├── models/
│   │   ├── chat.py
│   │   └── content.py
│   ├── orchestrator/
│   │   ├── deduplicator.py
│   │   ├── mixer.py
│   │   ├── orchestrator.py
│   │   ├── query_generator.py
│   │   ├── rank_placeholder.py
│   │   └── scrape_fetch.py
│   ├── redis/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── scrapers/
│   │   ├── instagram.py
│   │   ├── pinterest.py
│   │   └── youtube.py
│   └── main.py
├── Dockerfile
├── main.py
└── requirements.txt
```

---

## Top-level files

- **`main.py`**: Thin entrypoint that imports `app.main.app` so `uvicorn main:app` works.
- **`Dockerfile`**: Builds a small image running the FastAPI app with Uvicorn.
- **`requirements.txt`**: Python dependencies (FastAPI, Uvicorn, Redis, LiteLLM).

---

## Redis

Same Redis instance as Go. Set **`REDIS_URL`** (default `redis://localhost:6379`).

- **`app/config.py`**: Reads `REDIS_URL` from env.
- **`app/redis/client.py`**:
  - **`get_client()`**: Returns a Redis client (async).
  - **`get_shown_urls(user_id)`**: Returns set of already-shown URLs (for dedup). Go writes; Python reads.
  - **`get_preferences(user_id)`**: Returns user preferences dict (e.g. content_filter). Go reads+writes; Python reads.
  - **`get_search_cached(platform, query)`** / **`set_search_cached(platform, query, results)`**: Search cache `search:{query_hash}` (TTL 1 hour).

If Redis is unavailable, the helpers return empty set/dict or None so the app still runs.

---

## LLM (LiteLLM)

Primary and fallback models are read from env; LiteLLM handles provider routing (e.g. `openai/...`, `groq/...`).

- **`app/config.py`**: `LITELLM_PRIMARY_MODEL`, `LITELLM_FALLBACK_MODEL` (defaults: `openai/gpt-4o-mini`, `groq/llama-3-8b-8192`).
- **`app/llm/client.py`**: `generate_text(prompt)` calls LiteLLM `completion` with primary model; on failure tries fallback. Set `OPENAI_API_KEY`, `GROQ_API_KEY` (or other provider keys) in env as required by LiteLLM.

---

## `app/main.py`

- **`create_app()`**: Builds the FastAPI instance and attaches all routes.
- **`app`**: The FastAPI application object that Uvicorn runs.

Use this file if you want to add global middleware, CORS, etc.

---

## `app/api/routes.py`

Defines all **HTTP endpoints** exposed by this service.

- **`GET /health`**
  - Health check. Returns `{"status": "ok"}`.

- **`POST /agent/understand-soul`**
  - Request: `UnderstandSoulRequest` (`user_id`, `initial_prompt`).
  - Response: `UnderstandSoulResponse` (`user_id`, `soul`).
  - Behavior: trims and echoes the initial prompt as the soul (placeholder for LLM).

- **`POST /agent/generate-content`**
  - Request: `GenerateContentRequest` (`user_id`, `initial_prompt`, `enhanced_profile`, `preferences`, `recent_chats`, `limit`).
  - Response: `GenerateContentResponse` (`items`: list of `ContentItem`).
  - Behavior: full orchestrator flow (generate queries in ratio → cache-or-scrape concurrent → dedupe with Redis shown → rank placeholder → filter score ≥ 0.6 → mix by ratio → return up to `limit`).

- **`POST /agent/chat`**
  - Request: `ChatRequest` (user_id, message, user_goal, user_profile, chat_history, current_content_ids).
  - Response: `ChatResponse` (`chat_response`, `needs_new_content`, optional `search_queries`).
  - Behavior: LLM placeholder; returns a generic reply and `needs_new_content = true`.

This module is the **main integration surface** for the Go service.

---

## `app/models/`

### `app/models/chat.py`

Pydantic models describing the **agent contract** with the Go service.

- **`UnderstandSoulRequest` / `UnderstandSoulResponse`**: payloads for `/agent/understand-soul`.
- **`GenerateContentRequest`**: request for `/agent/generate-content` (user_id, initial_prompt, enhanced_profile, preferences, recent_chats, limit).
- **`Query`**: a single search query (`platform`, `query`); used optionally in `ChatResponse.search_queries`.
- **`ChatRequest` / `ChatResponse`**: payloads for `/agent/chat`.

These types mirror the Go `agent.Client` contracts.

### `app/models/content.py`

- **`ContentItem`**: matches Go `models.ContentItem` (id, type, platform, url, title, score, metadata).
- **`GenerateContentResponse`**: response for `/agent/generate-content` (`items`: list of `ContentItem`).

---

## `app/llm/`

Simple, swappable LLM helpers.

- **`client.py`**
  - **`LLMClient`** / **`generate_text(prompt)`**: LiteLLM completion with primary then fallback model; returns response or empty string.
  - This is where you would wire an actual LLM provider (e.g. LiteLLM, OpenAI, Groq).

- **`prompts.py`**
  - **`build_chat_prompt(message, initial_prompt, enhanced_profile, chat_history)`** and other build_*_prompt helpers per use case (see prompts.py).

- **`context_builder.py`**
  - **`build_content_context(items)`**: converts a list of `ContentItem`s into a compact string (currently just joins titles).

These helpers keep prompt-building and LLM calls isolated from the HTTP layer.

---

## `app/orchestrator/`

Full content flow: generate queries in ratio → cache-or-scrape (concurrent) → dedupe (Redis) → rank (placeholder) → filter score ≥ 0.6 → mix by ratio → return items.

- **`orchestrator.py`**
  - **`fetch_content(user_id, initial_prompt, enhanced_profile, preferences, recent_chats, limit=40)`**: main entry; runs the full pipeline and returns ranked `ContentItem`s.

- **`query_generator.py`**
  - **`generate_queries_ratio(initial_prompt, enhanced_profile, preferences, recent_chats)`**: returns queries in ratio (placeholder uses initial_prompt + enhanced_profile for query text).

- **`scrape_fetch.py`**
  - **`fetch_one_query(q)`**: for one query, returns cached raw results or scrapes then caches (Redis `search:{query_hash}`).

- **`rank_placeholder.py`**
  - **`rank_raw_items(raw, user_goal, user_profile)`**: placeholder rank (no LLM); assigns score 0.8 to each item.

- **`mixer.py`**
  - **`mix_by_ratio(items)`**: mixes by type: 16 image (8 Pinterest + 8 Instagram), 16 short (8 Reels + 8 Shorts), 8 video (YouTube).

- **`deduplicator.py`**
  - **`deduplicate(items)`**: in-memory URL dedup.
  - **`filter_already_shown_raw(raw, shown_urls)`**: filters out URLs in Redis `user:{id}:shown`.

---

## `app/scrapers/`

Pinterest, Instagram, YouTube only (placeholder mock data). Each returns a list of raw dicts (`id`, `type`, `platform`, `url`, `title`).

- **`pinterest.search(query)`** → mock image items.
- **`instagram.search(query, content_type="image"|"short")`** → mock photo or reel items.
- **`youtube.search(query, content_type="short"|"video")`** → mock shorts or video items.

---

## How to run the service

From the `python-service/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open in a browser:

- `http://localhost:8000/health` – health check
- `http://localhost:8000/docs` – interactive Swagger UI for all endpoints

