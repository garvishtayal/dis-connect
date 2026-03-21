# dis-connect

**Live:** [dis-connect.app](https://dis-connect.app)

**AI-assisted discovery** — personalized content from multiple sources, shaped by how you chat and what you save.

Sign in with Google (Firebase), explore a masonry feed, and refine results through conversation. A Go API orchestrates auth, users, preferences, and chat; a Python service handles ranking, LLM calls, and scraping. PostgreSQL and Redis sit underneath.

---

## Stack

| Layer | Technology |
|--------|------------|
| Web app | React 18, Vite 6, Tailwind CSS 4, TanStack Query, React Router |
| API | Go (Gin) — auth, content, chat, user state |
| Agent | Python — orchestration, ranking, LiteLLM (Groq / Gemini), scrapers |
| Data | PostgreSQL 16, Redis 7 |
| Identity | Firebase Authentication |

---

## Repository layout

```text
dis-connect/
├── frontend/          # SPA (Vite)
├── go-service/        # HTTP API
├── python-service/   # Agent & ranking
├── architecture/      # Diagrams & schema notes (Mermaid, SQL)
├── product-notes/     # Design notes
├── docker-compose.yml           # Pre-built images from Docker Hub
└── docker-compose.build.yml     # Build all services locally
```

Service-specific details: `go-service/README.md`, `python-service/README.md`.

---

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- For Hub deploy: a Docker Hub username and images tagged `youruser/dis-connect-{frontend,go,python}:latest`
- **Firebase**: client config for the frontend; Admin **service account JSON** for the Go API at `go-service/secret/firebase-service-account.json` (gitignored — do not commit)

---

## Configuration

1. Copy the example env and edit secrets:

   ```bash
   cp .env.example .env
   chmod 600 .env
   ```

2. Place Firebase Admin credentials at `go-service/secret/firebase-service-account.json`.

3. Set `DOCKERHUB_USERNAME` in `.env` when using `docker-compose.yml` with pulled images.

`VITE_*` variables are **baked into the frontend image at build time**. After changing them, rebuild and push the frontend image (or use `docker-compose.build.yml` locally).

---

## Run with pre-built images (Docker Hub)

Default compose binds services to **loopback only** (`127.0.0.1`): app **3000**, Go **8080**, Python **8000**, Postgres **5433**, Redis **6380**. Put a reverse proxy on the host for public HTTPS.

```bash
docker compose pull
docker compose up -d
```

---

## Build from source (local dev)

```bash
docker compose -f docker-compose.build.yml up --build
```

Compose reads `.env` for build args and runtime. For development **without** Docker, use per-service `.env` files as documented in each service README.

---

## Production notes

- Point DNS and your reverse proxy at **https://dis-connect.app** (or your host); static SEO in `frontend/index.html` and `public/sitemap.xml` use that canonical URL — update those files if the public domain changes.
- Replace default Postgres credentials in Compose (or use `docker-compose.override.yml`) for real deployments.
- Keep `.env` and `firebase-service-account.json` out of version control and restrict file permissions.

---

## Documentation

- [High-level architecture](architecture/01-high-level-architecture.md) — request flow and components
- [Database schema](architecture/05-database-schema.md) — tables and relationships
