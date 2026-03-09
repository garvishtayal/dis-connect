# dis-connect Go Service

This service is the **main API** for dis-connect. It handles **auth**, **users**, **content feed**, **chat**, and **preferences**, and delegates agent/content logic to the **Python service**.

It is built with **Gin** and follows a layered structure: handlers → services → repositories / external clients.

---

## Folder structure

```text
go-service/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── api/
│   │   ├── handlers/
│   │   │   ├── auth.go
│   │   │   ├── chat.go
│   │   │   ├── content.go
│   │   │   ├── health.go
│   │   │   ├── preferences.go
│   │   │   └── user.go
│   │   ├── middleware/
│   │   │   ├── cors.go
│   │   │   ├── firebase_auth.go
│   │   │   ├── logger.go
│   │   │   ├── onboarding.go
│   │   │   └── rate_limit.go
│   │   └── router.go
│   ├── app/
│   │   └── app.go
│   ├── agent/
│   │   └── agent.go
│   ├── auth/
│   │   ├── firebase.go
│   │   └── token_validator.go
│   ├── config/
│   │   └── config.go
│   ├── models/
│   │   ├── auth.go
│   │   ├── chat.go
│   │   ├── content.go
│   │   ├── search.go
│   │   └── user.go
│   ├── repository/
│   │   ├── postgres/
│   │   │   ├── client.go
│   │   │   ├── chat_repository.go
│   │   │   ├── content_repository.go
│   │   │   ├── user_repository.go
│   │   │   ├── preference_repository.go
│   │   │   └── migrations/
│   │   └── redis/
│   │       ├── client.go
│   │       └── dedup_repository.go
│   └── service/
│       ├── auth_service.go
│       ├── chat_service.go
│       ├── content_service.go
│       ├── preference_service.go
│       └── user_service.go
├── .env.example
├── Dockerfile
├── go.mod
└── go.sum
```

---

## Top-level files

- **`cmd/api/main.go`**: Entrypoint. Resolves port from config, builds the router via `app.BuildRouter()`, and runs the Gin server.
- **`Dockerfile`**: Multi-stage build (Go 1.22 Alpine → distroless). Produces a single `server` binary; exposes port 8080.
- **`go.mod`** / **`go.sum`**: Go module and dependencies (Gin, Firebase, PostgreSQL, Redis, etc.).
- **`.env.example`**: Example environment variables for local and deployment.

---

## Configuration

**`internal/config/config.go`** loads configuration from the environment (with defaults):

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | HTTP server port | `8080` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@localhost:5432/dis_connect?sslmode=disable` |
| `REDIS_ADDR` | Redis address | `localhost:6379` |
| `AGENT_BASE_URL` | Base URL of the Python agent service | `http://localhost:8000` |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | (required, no default) |

Helpers: **`NewPostgresDB(cfg)`** and **`NewRedisClient(cfg)`** create DB and Redis clients from `AppConfig`.

---

## `internal/app/app.go`

- **`BuildRouter()`**: Loads `.env`, validates Firebase credentials, creates Firebase client and token validator, Postgres client, repositories, and the **agent client** (using `AGENT_BASE_URL`), then wires all services and handlers. Attaches global middleware (logger, CORS), then registers all API routes. Returns the Gin engine or an error.
- **`ResolvePort()`**: Returns the port string for the server (used by `main`).

Use this file to add more middleware, new services, or change wiring.

---

## API routes (`internal/api/router.go`)

All routes are registered here. Protected routes require a valid **Firebase ID token** in `Authorization: Bearer <token>`. Some routes also require **onboarding completed** (user created with initial prompt).

| Method | Path | Auth | Onboarding | Handler | Description |
|--------|------|------|------------|---------|-------------|
| GET | `/healthz` | — | — | Health | Health check. Returns `{"status": "ok"}`. |
| POST | `/api/auth/google` | — | — | Auth | Sign in with Google (ID token). |
| POST | `/api/auth/apple` | — | — | Auth | Sign in with Apple (ID token). |
| POST | `/api/users` | Firebase | — | User | Create user (onboarding). Body: `initial_prompt`. Calls Python **understand-soul**; stores user and soul. |
| POST | `/api/chat` | Firebase | Required | Chat | Send chat message. Returns placeholder response (chat service can be wired to Python **agent/chat**). |
| GET | `/api/content` | Firebase | Required | Content | Get content feed. Query: `user_id`, optional `limit`, `offset`. Calls Python **agent** `/agent/generate-content` with user profile from Postgres. |
| POST | `/api/preferences` | Firebase | Required | Preferences | Update user preferences. Query: `user_id`; body: JSON preferences. Placeholder implementation. |

**Rate limiting** is applied to the `/api` group. **CORS** and **request logging** are applied globally.

---

## Handlers (`internal/api/handlers/`)

- **`health.go`**: `GET /healthz` → `{"status": "ok"}`.
- **`auth.go`**: `SignInWithGoogle`, `SignInWithApple` — bind `AuthRequest`, call `AuthService`, return token/user info.
- **`user.go`**: `CreateUser` — requires Firebase UID from context, binds `CreateUserRequest` (e.g. `initial_prompt`), calls `UserService.CreateUser` (which calls Python **understand-soul** and persists user).
- **`chat.go`**: `HandleChat` — binds `ChatRequest`, calls `ChatService.HandleChat` (currently placeholder).
- **`content.go`**: `GetContent` — binds query to `ContentRequest` (`user_id`, `limit`, `offset`), calls `ContentService.GetContent` (agent generate-content + user profile from Postgres).

---

## Middleware (`internal/api/middleware/`)

- **`logger.go`**: Request logging.
- **`cors.go`**: CORS configuration.
- **`rate_limit.go`**: Rate limiting for `/api`.
- **`firebase_auth.go`**: Validates `Authorization: Bearer <token>` with Firebase, sets `firebase_uid`, `email`, `provider`, `claims` in context. **`RequireFirebaseUID(c)`** extracts UID for handlers.
- **`onboarding.go`**: **OnboardingRequired** — after Firebase auth, checks Postgres that the user has completed onboarding; returns 403 if not. Applied to chat, content, and preferences.

---

## Auth (`internal/auth/`)

- **`firebase.go`**: **`NewFirebaseClient(ctx)`** — builds Firebase app from `FIREBASE_CREDENTIALS_PATH` (service account file).
- **`token_validator.go`**: **`NewTokenValidator(ctx, firebaseClient)`** — creates validator; **`VerifyIDToken(ctx, idToken)`** returns Firebase token claims.

Used by **AuthService** (sign-in) and **FirebaseAuth** middleware (protected routes).

---

## Agent client (`internal/agent/agent.go`)

HTTP client for the **Python agent service** (base URL from `AGENT_BASE_URL`). Used by **UserService**, **ContentService**, and **ChatService`.

- **`NewClient(baseURL)`**: Builds client with a timeout suitable for generate-content/chat.
- **`UnderstandSoul(ctx, req)`** → **`UnderstandSoulResponse`**: `POST /agent/understand-soul` — request: `user_id`, `initial_prompt`, `recent_chats`; response: `user_id`, `soul`.
- **`GenerateContent(ctx, req)`** → **`GenerateContentResponse`**: `POST /agent/generate-content` — full request (user_id, initial_prompt, enhanced_profile, preferences, recent_chats, limit); response: `items` (content list).
-- **`Chat(ctx, req)`** → **`ChatResponse`**: `POST /agent/chat` — request: user_id, message, initial_prompt, enhanced_profile, preferences, recent_chats; response: `chat_response`, `needs_new_content`.

Request/response types are defined in this package and mirror the Python agent contract.

---

## Models (`internal/models/`)

- **`user.go`**: **`User`** (id, firebase_uid, email, display_name, photo_url, provider, initial_prompt, onboarding_completed, soul). **`CreateUserRequest`** / **`CreateUserResponse`** for onboarding.
- **`content.go`**: **`ContentItem`** (id, type, platform, url, title, score, metadata). **`ContentRequest`** (user_id, limit, offset) for GET /api/content.
- **`chat.go`**: **`ChatMessage`**, **`ChatRequest`** (user_id, message), **`ChatResponse`** (chat_response, needs_new_content, new_content).
- **`auth.go`**: **`AuthRequest`**, **`AuthResponse`**, auth provider constants.

These types are used by handlers, services, and agent contracts.

---

## Services (`internal/service/`)

- **`auth_service.go`**: **AuthService** — sign-in with Google/Apple; validates token, creates or finds user, returns auth response.
- **`user_service.go`**: **UserService** — **CreateUser**: optionally calls **agent.UnderstandSoul** to get soul from initial prompt, then persists user via **UserRepository** (SetInitialPromptByFirebaseUID). Returns **CreateUserResponse** (user_id, soul, onboarding_completed).
- **`content_service.go`**: **ContentService** — **GetContent**: loads user profile (initial_prompt, enhanced_profile, preferences) via **UserRepository.GetContentProfileByUserID**, builds **agent.GenerateContentRequest**, calls **agent.Client.GenerateContent** (Python `/agent/generate-content`), returns items; applies offset client-side.
- **`chat_service.go`**: **ChatService** — **HandleChat**: placeholder; returns a fixed message and `needs_new_content: false`. Can be wired to **agent.Client.Chat**.

---

## Repositories

### Postgres (`internal/repository/postgres/`)

- **`client.go`**: **`NewClient(cfg)`** — wraps **config.NewPostgresDB**; used by all Postgres repos.
- **`user_repository.go`**: User CRUD; **SetInitialPromptByFirebaseUID** (create or update user with initial prompt and enhanced profile); **IsOnboardingCompletedByFirebaseUID** for onboarding middleware; **GetContentProfileByUserID** (initial_prompt, enhanced_profile, preferences) for the content service to call the agent generate-content API.
- **`chat_repository.go`**: Chat message history (if used).
- **`content_repository.go`**: Content cache / shown content (if used).
- **`preference_repository.go`**: Update user `preferences` JSONB in the `users` table.
- **`migrations/`**: **000001_init_schema** (users, chat_messages, shown_content, content_cache, indexes); **000002** adds **onboarding_completed** to users and makes **initial_prompt** nullable.

Same database can be used for users, chat, and content metadata; Redis is available for cache and dedup (see below).

### Redis (`internal/repository/redis/`)

- **`client.go`**: **`NewClient(cfg)`** — wraps **config.NewRedisClient**. Redis is configured in **config** and repositories exist; they are not yet wired in **app.go** but are available for:
- **`dedup_repository.go`**: **MarkShown(userID, url)**, **WasShown(userID, url)** — set/key `shown:{userID}` (e.g. for content dedup).

---

## How to run

1. **Environment**

   Copy `.env.example` to `.env` and set at least:

   - `FIREBASE_CREDENTIALS_PATH` — path to your Firebase service account JSON.
   - `DATABASE_URL` — Postgres connection string (run migrations first).
   - Optionally `REDIS_ADDR`, `AGENT_BASE_URL`, `PORT`.

2. **Database**

   Run Postgres migrations (e.g. with your migration tool or `psql`) in order:

   - `internal/repository/postgres/migrations/000001_init_schema.up.sql`
   - `internal/repository/postgres/migrations/000002_add_onboarding_completed_to_users.up.sql`

3. **Run the server**

   From the **`go-service/`** directory:

   ```bash
   go run ./cmd/api
   ```

   Default port is **8080**. Health check:

   - **`http://localhost:8080/healthz`**

4. **Docker**

   ```bash
   docker build -t go-service .
   docker run -p 8080:8080 --env-file .env go-service
   ```

   Ensure `.env` (or passed env) includes `FIREBASE_CREDENTIALS_PATH` and `DATABASE_URL`; mount the credentials file if needed.

---

## Summary

- **Go service** = main API (Gin): auth (Google/Apple via Firebase), user onboarding (with Python understand-soul), content feed (via agent generate-content + user profile from Postgres), chat and preferences (placeholders).
- **Python service** = agent/content engine: understand-soul, generate-content, chat; Go calls it via the **agent client**.
- **Postgres** = users, onboarding state, and (optionally) chat/content tables.
- **Redis** = configured; repos for dedup, preferences, and cache exist and can be wired in **app.go** when needed.
