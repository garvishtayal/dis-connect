# dis-connect Python Service

This service is the **agent / content engine** used by the Go API.  
It exposes HTTP endpoints that the Go service calls for:

- Understanding the user's **soul / goal**
- Generating **search queries** for external platforms
- **Ranking** raw content
- Handling **chat** logic
- Simple **content orchestration** for fetching and shaping items

The service is built with **FastAPI** and is intentionally simple and modular.

---

## Folder structure

```text
python-service/
├── app/
│   ├── api/
│   │   └── routes.py
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
│   │   └── orchestrator.py
│   ├── scrapers/
│   │   ├── instagram.py
│   │   ├── pinterest.py
│   │   ├── reddit.py
│   │   ├── unsplash.py
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
- **`requirements.txt`**: Python dependencies (FastAPI, Uvicorn).

---

## `app/main.py`

- **`create_app()`**: Builds the FastAPI instance and attaches all routes.
- **`app`**: The FastAPI application object that Uvicorn runs.

Use this file if you want to add global middleware, CORS, etc.

---

## `app/api/routes.py`

Defines all **HTTP endpoints** exposed by this service.

- **`GET /health`**
  - Simple health check. Returns `{"status": "ok"}`.

- **`POST /agent/understand-soul`**
  - Request: `UnderstandSoulRequest` (`user_id`, `initial_prompt`).
  - Response: `UnderstandSoulResponse` (`user_id`, `soul`).
  - Current behavior: trims and echoes the initial prompt as the soul.

- **`POST /agent/generate-queries`**
  - Request: `GenerateQueriesRequest` (`user_id`, `user_goal`, `user_profile`, `recent_chats`).
  - Response: `GenerateQueriesResponse` (list of `Query` objects).
  - Current behavior: returns simple placeholder queries for YouTube, Pinterest, and Reddit.

- **`POST /agent/rank`**
  - Request: `RankRequest` (`user_id`, `user_goal`, `user_profile`, `raw_results`).
  - Response: `RankResponse` (list of ranked `ContentItem`s).
  - Current behavior: normalizes each raw item, fills defaults, and sorts by score.

- **`POST /agent/chat`**
  - Request: `ChatRequest` (user, message, goal, profile, history, current content IDs).
  - Response: `ChatResponse` (chat text, `needs_new_content`, optional `search_queries`, optional `manifestation_tip`).
  - Current behavior: builds a simple LLM prompt, uses a placeholder LLM client, and always returns a generic reply with `needs_new_content = true`.

- **`POST /orchestrator/fetch-content`**
  - Request: `FetchContentRequest` (user, goal, profile, recent chats, queries).
  - Response: `FetchContentResponse` (list of `ContentItem`s).
  - Current behavior: passes queries to the orchestrator and returns placeholder content items.

This module is the **main integration surface** for the Go service.

---

## `app/models/`

### `app/models/chat.py`

Pydantic models describing the **agent contract** with the Go service.

- **`UnderstandSoulRequest` / `UnderstandSoulResponse`**: payloads for `/agent/understand-soul`.
- **`Query`**: a single search query (`platform`, `query`).
- **`GenerateQueriesRequest` / `GenerateQueriesResponse`**: payloads for `/agent/generate-queries`.
- **`RankRequest` / `RankResponse`**: payloads for `/agent/rank`.
- **`RankedItem`**: structured ranked item (id, type, platform, url, title, manifestation_note, score).
- **`ChatRequest` / `ChatResponse`**: payloads for `/agent/chat`.

These types mirror the Go `agent.Client` contracts.

### `app/models/content.py`

- **`ContentItem`**: normalized content item used inside the Python service and returned from the orchestrator.

---

## `app/llm/`

Simple, swappable LLM helpers.

- **`client.py`**
  - **`LLMClient`**: tiny wrapper with `generate_text(prompt, **kwargs)` returning a placeholder string.
  - This is where you would wire an actual LLM provider (e.g. LiteLLM, OpenAI, Groq).

- **`prompts.py`**
  - **`build_goal_prompt(user_goal, user_profile)`**: builds a simple text prompt from the goal and optional profile dict.

- **`context_builder.py`**
  - **`build_content_context(items)`**: converts a list of `ContentItem`s into a compact string (currently just joins titles).

These helpers keep prompt-building and LLM calls isolated from the HTTP layer.

---

## `app/orchestrator/`

Coordinates content fetching, mixing, and deduplication.

- **`orchestrator.py`**
  - **`fetch_content(queries)`**: async function that:
    - Takes a list of `Query` objects.
    - Currently creates **placeholder** `ContentItem`s (one per query).
    - Runs them through `mixer.mix()` and `deduplicator.deduplicate()`.
    - Returns the final list of `ContentItem`s.
  - This is the main place to plug in real scrapers + ranking later.

- **`mixer.py`**
  - **`mix(items)`**: sorts `ContentItem`s by score, highest first.

- **`deduplicator.py`**
  - **`deduplicate(items)`**: removes duplicate items by URL while preserving order.

---

## `app/scrapers/`

One module per external content source.  
All functions are **placeholders** for now and should be replaced with real HTTP logic.

- **`instagram.py`**
- **`pinterest.py`**
- **`reddit.py`**
- **`unsplash.py`**
- **`youtube.py`**

Each defines:

- **`async def search(query: str) -> list[dict[str, Any]]`**
  - Currently returns an empty list.
  - In the future, should:
    - Call the real API (or search endpoint).
    - Map results into a simple dict shape that can be turned into `ContentItem`s.

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

