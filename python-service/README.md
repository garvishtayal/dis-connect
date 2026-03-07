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
  - Health check. Returns `{"status": "ok"}`.

- **`POST /agent/understand-soul`**
  - Request: `UnderstandSoulRequest` (`user_id`, `initial_prompt`).
  - Response: `UnderstandSoulResponse` (`user_id`, `soul`).
  - Behavior: trims and echoes the initial prompt as the soul (placeholder for LLM).

- **`POST /agent/generate-content`**
  - Request: `GenerateContentRequest` (`user_id`, `user_goal`, `user_profile`, `recent_chats`, `current_content_ids`, `limit`).
  - Response: `GenerateContentResponse` (`items`: list of `ContentItem`).
  - Behavior: generates queries, runs orchestrator (scrape + mix + dedupe), returns up to `limit` items (placeholder).

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
- **`GenerateContentRequest`**: request for `/agent/generate-content` (user_id, user_goal, user_profile, recent_chats, current_content_ids, limit).
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

