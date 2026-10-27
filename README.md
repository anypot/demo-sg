# Demo SG App

A tiny full-stack demo: a static frontend served by Nginx and a FastAPI backend,
wired together with Docker Compose.

## Structure

- `frontend/` – Nginx serving `index.html` and proxying `/api/` to the backend
- `backend/` – FastAPI app with `/health` and `/hello` endpoints
- `docker-compose.yaml` – runs both services

## Run

```bash
docker compose up --build
```

Open <http://localhost:8080> and click the button to call the backend.

## Test & lint

From `backend/`: `pip install -r requirements-dev.txt && ruff check . && ruff format --check . && pytest`

## API

The backend serves these endpoints directly on port 8000:

- `GET /hello` → `{"message": "Backend response!", "version": "1.0"}`
- `GET /health` → `{"status": "ok"}`

The frontend nginx proxies the `/api/` prefix to the backend and strips it, so
through the frontend the same endpoints are reachable as `/api/hello` and
`/api/health` (`index.html` calls `/api/hello`).

FastAPI's interactive API docs are available at <http://localhost:8080/api/docs>
(and the OpenAPI schema at <http://localhost:8080/api/openapi.json>).

## CI and Git workflow

- **`dev`** – push runs ruff, pytest, then builds and pushes images tagged `dev-<sha>`.
- **Pull request → `main`** – runs ruff and pytest, builds both images, but does not push.
- **Merge to `main`** – triggers nothing by design.
- **Release** – tag `main` with `vX.Y.Z` and push the tag; CI builds and pushes images tagged `vX.Y.Z`.
- **Manual run** – `workflow_dispatch` on a branch behaves like a `dev` push
  (`dev-<sha>`); run on a `v*` tag and it behaves like a release.

Images are published to `ghcr.io/anypot/demo-sg/frontend:<tag>` and
`ghcr.io/anypot/demo-sg/backend:<tag>`, where `<tag>` is `dev-<sha>` for `dev`
pushes and `vX.Y.Z` for releases.
