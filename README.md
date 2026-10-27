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

## API

The backend serves these endpoints directly on port 8000:

- `GET /hello` → `{"message": "Backend response!"}`
- `GET /health` → `{"status": "ok"}`

The frontend nginx proxies the `/api/` prefix to the backend and strips it, so
through the frontend the same endpoints are reachable as `/api/hello` and
`/api/health` (`index.html` calls `/api/hello`).

FastAPI's interactive API docs are available at <http://localhost:8080/api/docs>
(and the OpenAPI schema at <http://localhost:8080/api/openapi.json>).
