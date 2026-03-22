# dis-connect Frontend

The **React SPA** for dis-connect. Handles authentication, one-time onboarding, and the main platform — a masonry content feed alongside a real-time goal advisor chat.

Built with **Vite + React 18**, styled with **Tailwind CSS v4**, and served in production by **Nginx** inside a Docker image.

---

## Folder structure

```text
frontend/
├── public/
│   ├── dino-game.html          # Chrome T-Rex game (used in footer)
│   ├── favicon.svg             # Generated from T-Rex sprite (build-favicon.mjs)
│   ├── apple-touch-icon.png    # Generated at build time
│   ├── logo-dis-connect.png
│   ├── logo-dis-connect-small.png
│   └── site.webmanifest
├── nginx/
│   └── default.conf            # Nginx config for the production container
├── scripts/
│   ├── build-favicon.mjs       # Extracts T-Rex sprite → favicon.svg
│   └── rasterize-apple-touch.mjs
├── src/
│   ├── api/                    # Thin fetch wrappers per resource
│   ├── components/
│   │   ├── layout/             # Footer, MobileBlock
│   │   ├── login/              # Logo, LoginCard, GoogleSignInButton
│   │   └── platform/           # Navbar, ContentFeed, ContentCard, ChatWindow, PlatformView, UpgradeModal
│   ├── hocs/                   # Route guards (auth, onboarding)
│   ├── hooks/                  # React Query hooks + Firebase auth
│   ├── lib/                    # firebase.js, session.js, authErrors.js
│   ├── pages/                  # Login, Initial, Platform
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── package.json
├── Dockerfile
└── .env.example
```

---

## Pages & routing

| Path | Page | Guard |
|------|------|-------|
| `/login` | Sign in with Google | Guest only (redirects away if already logged in) |
| `/initial` | One-time onboarding prompt | Onboarding pending required |
| `/platform` | Content feed + chat | Auth + onboarding done required |
| `/` | — | Redirects to `/login` |

Route guards are implemented as HOCs in `src/hocs/`:

- **`withGuestOnly`** — redirects logged-in users away from `/login`
- **`withAuthRequired`** — redirects unauthenticated users to `/login`
- **`withOnboardingPendingRequired`** — redirects to `/platform` if onboarding already done
- **`withOnboardingDoneRequired`** — redirects to `/initial` if onboarding not yet done

---

## Key components

### `src/pages/Login.jsx`
Google Sign-In via Firebase. On success, saves session to `localStorage` and navigates to `/platform` or `/initial` based on `onboarding_completed`.

### `src/pages/Initial.jsx`
One-time setup page. Displays a structured prompt for the user to copy into an LLM (ChatGPT, Claude, etc.) and paste the response back. The response is submitted to `POST /api/users` as `initial_prompt` to seed the personalisation profile.

### `src/pages/Platform.jsx`
Renders `PlatformView` — the full platform layout.

### `src/components/platform/PlatformView.jsx`
Main layout: `Navbar` (top) + `ContentFeed` (80% left) + `ChatWindow` (20% right, fixed).

### `src/components/platform/ContentFeed.jsx`
Masonry content feed (`react-responsive-masonry`, 5 columns). Calls `GET /api/content` on load and on scroll (infinite scroll). Listens to the `content:refresh` custom event dispatched by `ChatWindow` when new content is needed; dispatches `content:refresh:done` when complete.

### `src/components/platform/ChatWindow.jsx`
Fixed right-side advisor chat. On mount, sends a silent intro prompt to the backend and displays the personalised response. On each message, if the backend returns `needs_new_content: true`, triggers a feed refresh with up to **6 retries × 25s timeout** each before giving up.

### `src/components/layout/Footer.jsx`
Contains the embedded dino game (`dino-game.html` in an iframe) with a subtle "press space to jump" hint. Supports `light` and `dark` variants.

### `src/components/layout/MobileBlock.jsx`
Wraps the entire app. On screens below `md` (768px) it replaces the app with a humorous full-screen message — dis-connect is desktop-only.

---

## API layer (`src/api/`)

All API calls go through `src/api/client.js` — a thin `fetch` wrapper that:
- Reads `VITE_API_URL` at runtime (set to `/api` in production, proxied by Nginx to the Go service)
- Attaches a fresh Firebase ID token in `Authorization: Bearer` when `auth: true` is passed
- Throws on non-2xx responses with the backend's error message

| File | Endpoint |
|------|----------|
| `auth.js` | `POST /api/auth/google` |
| `user.js` | `POST /api/users` |
| `content.js` | `GET /api/content` |
| `chat.js` | `POST /api/chat` |

---

## Session (`src/lib/session.js`)

Lightweight `localStorage` helpers. Persists `user_id`, `email`, and `onboarding_completed` across page reloads. Does **not** store Firebase tokens — those are managed by the Firebase SDK and refreshed automatically.

---

## Configuration

All environment variables are **VITE_ prefixed** and get **baked into the JS bundle at build time** by Vite. Changing them requires a rebuild.

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Base URL for the Go API | `http://localhost:8080` |
| `VITE_FIREBASE_API_KEY` | Firebase web API key | — |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | — |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID | — |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket | — |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase sender ID | — |
| `VITE_FIREBASE_APP_ID` | Firebase app ID | — |

Copy `.env.example` to `.env` to get started locally.

---

## How to run

### Local development

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173`. Make sure `VITE_API_URL` in `.env` points to your Go service (default `http://localhost:8080`).

### Build for production

```bash
npm run build
```

This runs the favicon generation scripts first, then Vite builds into `dist/`.

### Docker

```bash
docker build \
  --build-arg VITE_API_URL=https://your-domain.com \
  --build-arg VITE_FIREBASE_API_KEY=... \
  -t dis-connect-frontend .
```

The Dockerfile is a two-stage build:
1. **Builder** — Node 22 Alpine, installs deps, builds the app
2. **Nginx** — copies `dist/` into `nginx:1.27-alpine`, serves on port 80

---

## Summary

- **React 18 + Vite** SPA with Tailwind CSS v4
- **Firebase** for Google auth; tokens are auto-refreshed, never stored manually
- **TanStack Query** for server state (content feed, chat, user creation)
- **Desktop-only** — mobile visitors see a humorous block screen instead of the app
- **Production** — static files served by Nginx; `/api` proxied to the Go service
