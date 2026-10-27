# Demo SG App

A tiny full-stack demo: a static frontend served by Nginx and a FastAPI backend,
wired together with Docker Compose.

## Structure

- `frontend/` – Nginx serving `index.html` and proxying `/api/` to the backend
- `backend/` – FastAPI app with `/health` and `/hello` endpoints
- `docker-compose.yaml` – runs both services
- `.github/workflows/` – `ci.yml` (validate, test, build, deploy dev) and
  `deploy-prod.yml` (manual prod deploy)
- `k8s/` – Kubernetes manifests: shared resources in `base/`, per-environment
  overlays in `overlays/dev` and `overlays/prod`

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

## Environments

Manifests live in `k8s/` and are built with Kustomize: `k8s/base` holds the
Deployments and Services, and each overlay adds its own namespace, image tags,
and any environment-specific settings.

- `k8s/overlays/dev` – namespace `demo-dev`, applied after every `dev` push
- `k8s/overlays/prod` – namespace `demo-prod`, applied by the `Deploy prod` workflow

Scaling: dev runs 2 fixed replicas per Deployment. Prod has a
HorizontalPodAutoscaler per Deployment (2–6 replicas, 70% CPU target), so the
base Deployments intentionally omit `replicas`.

Both overlays expose the Services as `ClusterIP`, so nothing is reachable from
outside the cluster: there is no ingress or TLS yet. To reach the app from your
machine:

```bash
kubectl port-forward -n demo-prod svc/frontend 8080:80
```

Then open <http://localhost:8080> (the frontend proxies `/api/` to the backend).

## CI and Git workflow

- **Validate** – before image builds and deployments, every run builds both overlays
  (`kustomize build k8s/overlays/dev` and `k8s/overlays/prod`), so broken
  manifests fail fast.
- **`dev`** – push runs ruff, pytest, then builds and pushes images tagged `dev-<sha>`.
- **Pull request → `main`** – runs ruff and pytest, builds both images, but does not push.
- **Merge to `main`** – triggers nothing by design.
- **Release** – tag `main` with `vX.Y.Z` and push the tag; CI builds and pushes images tagged `vX.Y.Z`.
- **Manual run** – `workflow_dispatch` on a branch behaves like a `dev` push
  (`dev-<sha>`); run on a `v*` tag and it behaves like a release.
- **Deploy (dev)** – after a `dev` push (or a manual run), CI sets the image tags in
  `k8s/overlays/dev` with `kustomize edit set image` and runs
  `kubectl apply -k k8s/overlays/dev` against the AKS cluster. Tag pushes do not deploy.
- **Deploy (prod)** – run the `Deploy prod` workflow manually from `main` with a release
  tag (`gh workflow run deploy-prod.yml --ref main -f image_tag=vX.Y.Z`); it pins the prod
  overlay to that tag's images and applies it.

CI authenticates to Azure Container Registry using these secrets in the
`azure` environment:

- `ACR_LOGIN_SERVER` – registry hostname, e.g. `myregistry.azurecr.io`
- `ACR_USERNAME` – ACR admin username or service-principal app ID
- `ACR_PASSWORD` – ACR admin password or service-principal secret

## Notes

- A package manager such as Poetry or uv (with a lock file) is not used yet;
  adopting one is good practice for reproducible builds.
- The current ACR login uses long-lived credentials, which is fine for a demo. The long-term solution is to use Azure OIDC with federated credentials instead of the stored static secrets.
- The prod ingress uses `webapprouting.kubernetes.azure.com`, but the app
  routing add-on does not install cert-manager. Either install cert-manager and
  create a `letsencrypt-prod` ClusterIssuer, or remove the
  `cert-manager.io/cluster-issuer` annotation and provide the `demo-tls` secret
  another way (e.g. Key Vault).
- The ingress host is a placeholder (`demo.example.com`); change it in
  `k8s/overlays/prod/ingress.yaml` and point that DNS name at the ingress
  address before expecting TLS to work.
- The AKS cluster is too small to host the prod overlay (2 replicas per
  Deployment plus the ingress controller) and the exercise's 4-hour limit does
  not allow for the required provisioning delays, so the prod manifests are
  illustrative and only dev is actually deployed.
