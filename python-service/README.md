# dis-connect Python Service

A deliberately **thin service** with two responsibilities:

1. **LLM agent** — query generation, chat, soul understanding, preferences (via LiteLLM)
2. **Scraper executor** — runs YouTube and Pinterest scrapes on demand, called by Go worker pools

All orchestration lives in the Go service. Python has **no Redis dependency**, no queue logic, no mixing, no deduplication. It is a pure executor.

Built with **FastAPI + LiteLLM + Uvicorn**.

---

## How it fits in the system

```
Go Service
   │
   ├── LLM calls (blocking, synchronous)
   │     POST /agent/generate-queries   → 4 search queries from user profile
   │     POST /agent/understand-soul    → enhanced profile from initial prompt
   │     POST /agent/chat               → LLM reply + needs_new_content flag
   │     POST /agent/prefrences         → updated preferences JSON
   │
   └── Scraper calls (from Go worker pools, concurrent)
         POST /scraper/youtube          → list of ContentItem
         POST /scraper/pinterest        → list of ContentItem (proxy optional)
```

Python never initiates anything — it only responds to Go's calls.

---

## Folder structure

```text
python-service/
├── app/
│   ├── api/
│   │   ├── routes.py            LLM agent endpoints (/agent/*)
│   │   └── scraper_routes.py    scraper endpoints (/scraper/*)
│   ├── llm/
│   │   ├── client.py            LiteLLM wrapper with primary + fallback model chain
│   │   ├── prompts.py           all system prompts and build_*_prompt helpers
│   │   └── query_generator.py   LLM → parse → enforce 2 Pinterest + 2 YouTube
│   ├── models/
│   │   ├── chat.py              Pydantic request/response models (agent contract)
│   │   └── content.py           ContentItem model
│   ├── scrapers/
│   │   ├── pinterest.py         pinscrape wrapper — 25 items per query, proxy support
│   │   ├── youtube.py           YouTube Data API v3 — 50 shorts + 30 videos per query
│   │   └── models.py            raw scraper output types
│   ├── services/
│   │   ├── agent_service.py     LLM orchestration for each agent endpoint
│   │   └── scraper_service.py   converts raw scraper output to ContentItem
│   ├── config.py                reads env vars (models, API keys)
│   └── main.py                  FastAPI app factory + exception handlers
├── main.py                      thin entrypoint for uvicorn main:app
├── Dockerfile
└── requirements.txt
```

---

## Endpoints

### Agent endpoints — called by Go service for LLM tasks

#### `GET /health`
Returns `{"status": "ok"}`. Used by Go service to verify Python is reachable.

---

#### `POST /agent/generate-queries`

Called by `ContentService` in Go at the start of every content feed request.

**Request** (`GenerateContentRequest`):
```json
{
  "user_id": "abc123",
  "initial_prompt": "I want to become a principal engineer at a top company",
  "enhanced_profile": "...",
  "preferences": { "content_filter": ["image", "short", "video"] },
  "recent_chats": [{"role": "user", "content": "show me more system design content"}]
}
```

**Response** (`list[Query]`):
```json
[
  {"platform": "pinterest", "query": "senior backend architect workspace"},
  {"platform": "pinterest", "query": "principal engineer lifestyle inspiration"},
  {"platform": "youtube", "query": "principal engineer day in my life #shorts"},
  {"platform": "youtube", "query": "system design deep dive staff engineer"}
]
```

**Behaviour**: Builds a prompt from the user profile and recent chat history, calls the LLM, parses the JSON array response, and enforces exactly 2 Pinterest + 2 YouTube queries. If the most recent chat message is a content request that aligns with the user's goal, it takes priority over the profile-based queries. If it doesn't align, the LLM is instructed to decline and redirect.

---

#### `POST /agent/understand-soul`

Called by Go's `UserService` during onboarding.

**Request**: `user_id`, `initial_prompt`, `recent_chats`
**Response**: `user_id`, `soul` (enhanced profile string)

Calls the LLM with the user's raw initial prompt to derive a richer, structured understanding of who they are and what they're building toward. The result is stored in Postgres as `enhanced_profile`.

---

#### `POST /agent/chat`

Called by Go's `ChatService` on every chat message.

**Request**: `user_id`, `message`, `initial_prompt`, `enhanced_profile`, `preferences`, `recent_chats`
**Response**: `chat_response` (string), `needs_new_content` (bool)

The LLM acts as a warm mentor (see the `chat` system prompt in `prompts.py`). The response is parsed for a structured `needs_new_content` signal — if the user is requesting new content, Go will trigger a fresh `GET /api/content`.

---

#### `POST /agent/prefrences`

Called by Go's `ChatService` in a background goroutine every 5 messages.

**Request**: `user_id`, `preferences` (current), `recent_chats`
**Response**: `preferences` (updated JSON object)

The LLM extracts or updates the user's content preference JSON based on their recent chat messages. Result is persisted to Postgres by Go.

---

### Scraper endpoints — called by Go worker pools

These are called concurrently by Go workers. Python does not queue, cache, or aggregate — it just scrapes and returns.

#### `POST /scraper/youtube`

**Request**: `{ "query": "principal engineer day in my life #shorts" }`
**Response**: `list[ContentItem]`

Calls the YouTube Data API v3. Returns up to 50 shorts and 30 videos per query. Each item has `id`, `type` (`short` or `video`), `platform`, `url`, `title`.

---

#### `POST /scraper/pinterest`

**Request**: `{ "query": "senior architect workspace", "proxy": "http://..." }`
**Response**: `list[ContentItem]`

Uses `pinscrape` to scrape Pinterest search results. Returns up to 25 image items. The `proxy` field is optional — passed by Go workers when `PINTEREST_PROXY_URL` is configured.

---

## LLM — `app/llm/`

### `client.py`

`generate_text(prompt)` tries models in order (primary → fallbacks). Returns the first non-empty response. Raises `LLMError` if all models fail. Prints `[llm] {model}` to stdout on success so you can see which model handled each request.

Configure models via env:
```
LITELLM_PRIMARY_MODEL=groq/llama-3.1-8b-instant
LITELLM_FALLBACK_MODEL=openai/gpt-4o-mini
```

LiteLLM handles provider routing — set the appropriate API key for whichever provider you use (`GROQ_API_KEY`, `OPENAI_API_KEY`, etc.).

### `prompts.py`

Contains all system prompts as strings in `SYSTEM_PROMPTS` dict and a `build_*_prompt` helper per use case:

- `SYSTEM_PROMPTS["chat"]` — mentor personality, tone, and rules for the advisor
- `SYSTEM_PROMPTS["query_generation"]` — content quality rules, domain examples, chat-first logic, strict JSON-only output instructions
- `build_query_generation_prompt(initial_prompt, enhanced_profile, preferences, chat_history)` — assembles the user-turn prompt for query generation
- `build_chat_prompt(message, initial_prompt, enhanced_profile, chat_history)` — assembles the user-turn prompt for chat
- `build_enhance_profile_prompt(initial_prompt, chat_history)` — prompt for understand-soul
- `build_preferences_prompt(chat_history, preferences)` — prompt for preferences update

### `query_generator.py`

`generate_queries_ratio(initial_prompt, enhanced_profile, preferences, recent_chats)`:
1. Builds full prompt (system + user)
2. Calls `generate_text`
3. Strips markdown fences if present
4. Parses JSON array
5. Enforces platform limits (max 2 Pinterest, max 2 YouTube)
6. Prints each accepted query: `[query] {platform}: {query}`
7. Raises `ValueError` on parse failure (caught by FastAPI → returns 400)

---

## Scrapers — `app/scrapers/`

### `youtube.py`

Uses YouTube Data API v3. `search(query)` makes two API calls:
- Search for `#shorts` — returns up to 50 results
- Search for regular videos — returns up to 30 results

Each result becomes a dict with `id`, `type` (`short` or `video`), `platform` (`youtube`), `url` (YouTube watch URL), `title`.

Requires `YOUTUBE_API_KEY` env var.

### `pinterest.py`

Uses `pinscrape`. `search(query, proxy_url="")` runs synchronously in a thread executor to avoid blocking the event loop.

- Returns up to 25 image items
- If `proxy_url` is provided, builds a proxy dict compatible with `pinscrape`'s requests session
- `pinscrape` writes a `data/time_epoch.json` file to track inter-request timing for rate limiting — this file is excluded from git and Docker

---

## Services — `app/services/`

### `agent_service.py`

Thin orchestration layer. Each function maps one-to-one to an endpoint:

- `understand_soul(req)` → calls `build_enhance_profile_prompt` + LLM
- `generate_queries(req)` → calls `generate_queries_ratio` from `app.llm.query_generator`
- `chat(req)` → calls `build_chat_prompt` + LLM + `parse_chat_response`
- `preferences(req)` → calls `build_preferences_prompt` + LLM + JSON parse

### `scraper_service.py`

Converts raw scraper dicts to `ContentItem` Pydantic objects. Called by the scraper route handlers.

---

## Exception handling — `app/main.py`

Custom exception handlers map Python exceptions to HTTP status codes:

| Exception | Status code |
|---|---|
| `LLMError` | 503 Service Unavailable |
| `ValueError` | 400 Bad Request |
| `RuntimeError` | 503 Service Unavailable |
| Any other `Exception` | 500 Internal Server Error |

This means a failed JSON parse from the LLM returns 400 (not 500), which Go handles gracefully.

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `LITELLM_PRIMARY_MODEL` | Primary LLM model | `openai/gpt-4o-mini` |
| `LITELLM_FALLBACK_MODEL` | Fallback model | `groq/llama-3-8b-8192` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `GROQ_API_KEY` | Groq API key | — |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | required for scraping |

---

## How to run

```bash
# From python-service/
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env  # fill in API keys

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health check: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs` — useful for testing endpoints manually

**Docker:**

```bash
docker build -t dis-connect-python .
docker run -p 8000:8000 --env-file .env dis-connect-python
```
