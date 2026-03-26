# dis-connect Go Service

The **main API** for dis-connect. It handles authentication, user onboarding, the content feed, chat, and upgrade flows. It is the orchestration brain of the system — all content generation, caching, queuing, and deduplication happen here. The Python service is called only for LLM tasks and scraping execution.

Built with **Gin** and follows a strict layered structure: HTTP handlers → services → repositories and external clients.

---

## How it fits in the system

```
Frontend
   │
   ▼
Go Service  ──── LLM tasks (query gen, chat, soul) ────►  Python Service
   │                                                          │
   ├── content orchestration                          /agent/generate-queries
   │     Redis queues + worker pools                  /agent/chat
   │     aggregator + mixer                           /agent/understand-soul
   │     dedup + rate limits                         /scraper/youtube
   │                                                  /scraper/pinterest
   ├── Postgres  (users, chat history, preferences)
   └── Redis     (queues, cache, dedup, rate limits)
```

The Go service owns all business logic. Python is a thin executor.

---

## Folder structure

```text
go-service/
├── cmd/
│   └── api/
│       └── main.go                 entrypoint — starts Gin server
├── internal/
│   ├── app/
│   │   └── app.go                  bootstrap: wires all deps, starts worker pools, builds router
│   ├── api/
│   │   ├── router.go               registers all routes
│   │   ├── handlers/
│   │   │   ├── auth.go             sign-in with Google / Apple
│   │   │   ├── user.go             create user (onboarding)
│   │   │   ├── content.go          GET /api/content
│   │   │   ├── chat.go             POST /api/chat
│   │   │   ├── upgrade.go          upgrade plan endpoints
│   │   │   └── health.go           GET /healthz
│   │   └── middleware/
│   │       ├── firebase_auth.go    validates Firebase ID token
│   │       ├── onboarding.go       requires completed onboarding
│   │       ├── cors.go
│   │       ├── logger.go
│   │       └── rate_limit.go
│   ├── agent/
│   │   └── agent.go                HTTP client → Python LLM endpoints
│   ├── auth/
│   │   ├── firebase.go             Firebase app init
│   │   └── token_validator.go      Firebase ID token verification
│   ├── config/
│   │   └── config.go               loads env vars into AppConfig
│   ├── content/                    all content-generation machinery
│   │   ├── aggregator/
│   │   │   └── aggregator.go       polls Redis until all scrape jobs done
│   │   ├── mixer/
│   │   │   └── mixer.go            mix + rank + dedup by ratio
│   │   ├── queue/
│   │   │   ├── jobs.go             ScrapeJob struct
│   │   │   └── redis_queue.go      LPUSH / BRPOP queue operations
│   │   ├── scraper/
│   │   │   └── client.go           HTTP client → Python /scraper/* endpoints
│   │   └── worker/
│   │       └── pool.go             YouTube pool (5) + Pinterest pool (2, 1.5s delay)
│   ├── models/                     shared domain types
│   │   ├── user.go
│   │   ├── content.go
│   │   ├── chat.go
│   │   ├── auth.go
│   │   ├── search.go
│   │   └── upgrade.go
│   ├── repository/
│   │   ├── postgres/
│   │   │   ├── client.go
│   │   │   ├── user_repository.go
│   │   │   ├── chat_repository.go
│   │   │   ├── preference_repository.go
│   │   │   ├── upgrade_repository.go
│   │   │   └── migrate.go          auto-runs SQL migrations on startup
│   │   └── redis/
│   │       ├── client.go
│   │       ├── dedup_repository.go
│   │       ├── rate_limit_repository.go
│   │       ├── request_state_repository.go
│   │       └── search_cache_repository.go
│   └── service/
│       ├── content_service.go
│       ├── chat_service.go
│       ├── auth_service.go
│       ├── user_service.go
│       ├── upgrade_service.go
│       └── user_id_resolver.go
├── .env.example
├── Dockerfile
└── go.mod
```

---

## Configuration

`internal/config/config.go` reads from environment on startup:

| Variable | Description | Default |
|---|---|---|
| `PORT` | HTTP server port | `8080` |
| `DATABASE_URL` | Postgres connection string | `postgres://postgres:postgres@localhost:5432/dis_connect?sslmode=disable` |
| `REDIS_ADDR` | Redis address | `localhost:6379` |
| `AGENT_BASE_URL` | Python service base URL | `http://localhost:8000` |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | required |
| `PINTEREST_PROXY_URL` | Optional HTTP proxy URL for Pinterest workers | `""` |

---

## Startup — `internal/app/app.go`

`BuildRouter()` is the single bootstrap function. It:

1. Loads `.env` (once)
2. Validates Firebase credentials file is readable
3. Creates Firebase client + token validator
4. Connects to Postgres, runs auto-migrations
5. Creates all Postgres repositories (user, chat, preference, upgrade)
6. Connects to Redis, creates all Redis repositories (dedup, rate limit, request state, search cache)
7. Creates the Redis queue, Python scraper HTTP client, and aggregator
8. **Starts background worker pools** (YouTube: 5 goroutines, Pinterest: 2 goroutines — run for the lifetime of the process)
9. Creates all services and handlers
10. Wires and returns the Gin engine

---

## API routes

All routes live in `internal/api/router.go`.

| Method | Path | Auth | Onboarding | Description |
|---|---|---|---|---|
| GET | `/healthz` | — | — | Returns `{"status":"ok"}` |
| POST | `/api/auth/google` | — | — | Sign in with Google Firebase token |
| POST | `/api/auth/apple` | — | — | Sign in with Apple Firebase token |
| POST | `/api/users` | Firebase | — | Create user during onboarding. Calls Python `/agent/understand-soul` to derive enhanced profile, persists user |
| GET | `/api/content` | Firebase | ✓ | Fetch content feed (queue-based, see below) |
| POST | `/api/chat` | Firebase | ✓ | Send chat message. LLM reply + optional content refresh signal |
| POST | `/api/upgrade` | Firebase | ✓ | Upsert user upgrade plan |
| GET | `/api/upgrade` | Firebase | ✓ | Get user upgrade plan |

**Firebase auth** middleware validates the `Authorization: Bearer <token>` header and sets `firebase_uid` in context.

**Onboarding** middleware checks Postgres that `onboarding_completed = true` before allowing access to content and chat.

---

## Content generation flow — `internal/service/content_service.go`

This is the heart of the system. Every `GET /api/content` request goes through this flow:

```
1. Resolve internal user ID (Firebase UID → Postgres user ID)
2. Check daily rate limit (Redis counter — 10 requests/day)
3. Load user profile from Postgres (initial_prompt, enhanced_profile, preferences)
4. Call Python /agent/generate-queries — LLM returns 4 queries (2 Pinterest, 2 YouTube)
5. For each query:
     - Cache hit  → add items to cachedItems immediately
     - Cache miss → create ScrapeJob and push to Redis queue
6. If any pending jobs:
     - Init request state in Redis (total job count)
     - Push jobs to queue:youtube or queue:pinterest
     - Aggregator polls Redis every 300ms until all jobs done or 8s timeout
7. Load user's shown URLs from Redis dedup set
8. mixer.Mix(cachedItems + scraped, shownURLs, limit)
     Ratio: 40% Pinterest images | 40% YouTube shorts | 20% YouTube videos
     Fresh content first; up to 40% of already-shown allowed to repeat
9. Persist returned URLs to Redis dedup set (MarkShownBatch)
10. Return items
```

**Cold request** (no cache): ~4 seconds. **Cache hit**: under 1 second.

---

## Worker pools — `internal/content/worker/pool.go`

Two pools start at boot and run forever:

**YouTube pool** — 5 goroutines
- Blocks on `BRPOP queue:youtube` (2s timeout, loops back if empty)
- Calls Python `POST /scraper/youtube` with the query
- Stores results in Redis search cache + request results list
- Increments `req:{id}:done` counter

**Pinterest pool** — 2 goroutines
- Same flow but on `queue:pinterest`
- Enforces a **1.5 second delay** after each job to avoid Pinterest rate limits
- Accepts an optional proxy URL (set via `PINTEREST_PROXY_URL` env var)

Workers are fire-and-forget goroutines. The aggregator is what connects them back to the waiting HTTP request.

---

## Aggregator — `internal/content/aggregator/aggregator.go`

After jobs are queued, the HTTP handler calls `aggregator.Wait(ctx, requestID, totalJobs, 8s)`.

The aggregator polls `req:{id}:done` in Redis every **300ms**. When `done >= total`, or the 8-second timeout elapses, it reads all results from `req:{id}:results` and returns them. On timeout it returns whatever partial results are available — the request never blocks indefinitely.

---

## Mixer — `internal/content/mixer/mixer.go`

Takes the flat pool of all items (cached + freshly scraped) and produces the final ordered list:

- **Bucketing**: items split into `images` (Pinterest), `shorts`, `videos` (YouTube)
- **Ratio**: 40% images, 40% shorts, 20% videos (of `limit`)
- **Ranking**: YouTube items preserve API relevance order within each bucket
- **Deduplication**: within-batch URL dedup; cross-request dedup against `shownURLs`
- **Repeat allowance**: up to 40% of the result can be already-shown content (so the feed doesn't go empty after a few requests)

---

## Chat — `internal/service/chat_service.go`

`HandleChat` flow:
1. Resolves internal user ID
2. Checks daily rate limit (20 messages/day per user)
3. Loads user profile + last 5 chat messages from Postgres
4. Calls Python `/agent/chat` → LLM reply + `needs_new_content` flag
5. Saves both user and agent messages to Postgres chat history
6. Every 5th message: **background goroutine** calls Python `/agent/prefrences` to update the user's content preference JSON in Postgres (non-blocking)
7. Returns reply immediately; if `needs_new_content=true`, the frontend is expected to trigger a new `GET /api/content`

---

## Agent client — `internal/agent/agent.go`

HTTP client for all Python LLM endpoints. Uses a 90-second timeout.

| Method | Python endpoint | Used by |
|---|---|---|
| `GenerateQueries` | `POST /agent/generate-queries` | ContentService |
| `UnderstandSoul` | `POST /agent/understand-soul` | UserService |
| `Chat` | `POST /agent/chat` | ChatService |
| `Preferences` | `POST /agent/prefrences` | ChatService (background) |

---

## Repositories

### Postgres (`internal/repository/postgres/`)

- **`user_repository.go`** — create/upsert users; `GetContentProfileByUserID` loads `initial_prompt`, `enhanced_profile`, `preferences` for content and chat; `SetInitialPromptByFirebaseUID` completes onboarding.
- **`chat_repository.go`** — `SaveMessage`, `ListMessages`, `CountMessages` for chat history.
- **`preference_repository.go`** — `UpdatePreferences` writes the JSONB preferences column.
- **`upgrade_repository.go`** — upsert/get upgrade plan rows.
- **`migrate.go`** — runs embedded SQL migrations automatically on startup via `golang-migrate`.

### Redis (`internal/repository/redis/`)

- **`dedup_repository.go`** — `GetShownURLs` / `MarkShownBatch` for cross-request content deduplication. Key: `user:{uid}:shown`.
- **`rate_limit_repository.go`** — `AllowDaily(key, limit)` using Redis `INCR` + `EXPIRE`. Used for both chat (20/day) and content (10/day) quotas.
- **`request_state_repository.go`** — `Init`, `IncrDone`, `AppendResults`, `GetProgress`, `GetResults`. Manages per-request worker progress. Keys: `req:{id}:total`, `req:{id}:done`, `req:{id}:results` (5-minute TTL).
- **`search_cache_repository.go`** — `Get` / `Set` for scrape result caching by platform + query. Key: `search:{sha256_hash[:16]}` (1-hour TTL).

---

## Redis key schema

| Key pattern | Type | TTL | Purpose |
|---|---|---|---|
| `queue:youtube` | List | — | YouTube scrape job queue |
| `queue:pinterest` | List | — | Pinterest scrape job queue |
| `req:{id}:total` | String | 5 min | Total jobs for a request |
| `req:{id}:done` | String | 5 min | Completed job counter |
| `req:{id}:results` | List | 5 min | Scraped result items (JSON) |
| `search:{hash}` | String | 1 hour | Scrape result cache |
| `user:{uid}:shown` | Set | — | Shown URL dedup set per user |
| `rl:content:{uid}:{date}` | String | 1 day | Content rate limit counter |
| `rl:chat:{uid}:{date}` | String | 1 day | Chat rate limit counter |

---

## How to run

```bash
# From go-service/
cp .env.example .env
# Fill in: FIREBASE_CREDENTIALS_PATH, DATABASE_URL, REDIS_ADDR, AGENT_BASE_URL

go run ./cmd/api
```

- Server starts on port `8080` by default
- Postgres migrations run automatically on startup
- Worker pools start automatically at boot
- Health check: `http://localhost:8080/healthz`

**Docker:**

```bash
docker build -t dis-connect-go .
docker run -p 8080:8080 --env-file .env dis-connect-go
```
