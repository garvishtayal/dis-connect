## dis-connect

AI-powered personalized content discovery app with chat-driven preferences and multi-source search.

### Folder structure

```bash
dis-connect/
├── frontend/        # React + CopilotKit UI
├── go-service/      # Go API (search + orchestration)
├── python-service/  # Python agent service (ranking + scraping support)
├── architecture/    # Architecture & schema diagrams (Mermaid + SQL)
├── docker-compose.yml
└── product-notes/   # Design notes and sketches
```

Create **one** **`.env` at the repo root** from **`.env.example`**, fill in secrets, then:

```bash
docker compose up --build
```

Compose **automatically** reads **`.env`** next to `docker-compose.yml`: it supplies **`${VITE_*}`** for the **frontend build** and **`env_file`** for **go-service** and **python-service**. No `--env-file` flag needed.

For **local dev without Docker**, you can still use per-app files (`frontend/.env`, `go-service/.env`, `python-service/.env` from each `.env.example`).

Postgres and Redis are published on host **`5433`** and **`6380`** so they don’t conflict with a local Postgres/Redis on 5432/6379. Apps in Compose still talk to **`postgres:5432`** and **`redis:6379`** on the internal network.

### Docker Compose and `.env` files

| Service | Config | Purpose |
|--------|--------|--------|
| **All** | **`.env`** (repo root) | Single file: **`VITE_*`**, Go, and Python variables. Compose **`environment`** overrides DB/Redis/agent/Firebase paths for Docker. |
| **frontend** | Build args from root `.env` | Static bundle; not copied into image (`frontend/.dockerignore`). |

On a VM:

1. Clone the repo (e.g. `/opt/dis-connect`).
2. `cp .env.example .env` and fill in keys; `chmod 600 .env`
3. `docker compose up -d --build`

**Go + Firebase:** put your Firebase Admin **service account JSON** at **`go-service/secret/firebase-service-account.json`** (download from Firebase Console → Project settings → Service accounts). Compose mounts `./go-service/secret` into the container at `/app/secret` read-only. Do not commit this file (it is gitignored).

For production Postgres, replace dev defaults in Compose (or use `docker-compose.override.yml`) with strong passwords and matching `DATABASE_URL`.

