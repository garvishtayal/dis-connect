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

Create **one** **`.env` at the repo root** from **`.env.example`**, fill in secrets.

### Docker Hub (default `docker-compose.yml`)

Images: **`${DOCKERHUB_USERNAME}/dis-connect-frontend:latest`**, **`dis-connect-go:latest`**, **`dis-connect-python:latest`**. Set **`DOCKERHUB_USERNAME`** in `.env`, then:

```bash
docker compose pull
docker compose up -d
```

App ports bind to **loopback only** (`127.0.0.1:3000`, `:8080`, `:8000`, `:5433`, `:6380`) — put a reverse proxy on the host for public HTTPS. **`VITE_*`** is baked into the frontend image when you **build and push**; update image tags after config changes.

### Build from source (local dev)

```bash
docker compose -f docker-compose.build.yml up --build
```

Compose reads **`.env`** for **`env_file`** and **`${VITE_*}`** build args on the frontend service.

For **local dev without Docker**, you can still use per-app `.env` files under each service.

### Docker Compose and `.env` files

| Service | Config | Purpose |
|--------|--------|--------|
| **Hub deploy** | **`.env`** | **`DOCKERHUB_USERNAME`**, Go/Python secrets; **`env_file`** for go + python. |
| **Build compose** | **`.env`** | **`VITE_*`**, Go, Python; Compose **`environment`** overrides DB/Redis/agent/Firebase for Docker. |

On a VM (Hub):

1. Clone the repo, add **`go-service/secret/firebase-service-account.json`**, `cp .env.example .env`, set **`DOCKERHUB_USERNAME`** and API keys, `chmod 600 .env`
2. `docker compose pull && docker compose up -d`

**Go + Firebase:** put your Firebase Admin **service account JSON** at **`go-service/secret/firebase-service-account.json`** (download from Firebase Console → Project settings → Service accounts). Compose mounts `./go-service/secret` into the container at `/app/secret` read-only. Do not commit this file (it is gitignored).

For production Postgres, replace dev defaults in Compose (or use `docker-compose.override.yml`) with strong passwords and matching `DATABASE_URL`.

