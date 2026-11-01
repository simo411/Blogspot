# Blogspot

A blogging app: register, log in, write posts, read everyone else's.

**v2** rebuilds the backend as separate containerised services, with a FastAPI API, a dedicated schema/migration service, CI that tests everything against real MySQL, and Kubernetes manifests. The original v1 (a React app + a single Express file) is preserved on the [`main`](../../tree/main) branch. See [From v1 to v2](#from-v1-to-v2) for what changed and why.

## Architecture

```
                 ┌───────────────────────────────────────┐
  Browser ─────▶ │ web          nginx + React build      │  the "main face"
                 │   /        → static app (SPA)         │
                 │   /api/*   → blog-api                 │  same origin: no CORS,
                 └───────────────────┬───────────────────┘  no hardcoded URLs
                                     ▼
                 ┌───────────────────────────────────────┐
                 │ blog-api     FastAPI                  │  read/write service
                 │   auth (JWT) · users · blogs          │  stateless → scales
                 │   /healthz (live) · /readyz (ready)   │  horizontally
                 └───────────────────┬───────────────────┘
                                     ▼
  ┌──────────────────────┐   ┌───────────────────────────┐
  │ db-migrations        │──▶│ mysql 8.4                 │
  │ Alembic, runs once   │   │ own volume / PVC          │
  │ when MySQL is up,    │   └───────────────────────────┘
  │ then exits           │
  └──────────────────────┘
```

**Startup order is enforced, not hoped for:**
`mysql` healthy → `db-migrations` exits 0 → `blog-api` ready → `web`.
In Kubernetes the same guarantee comes from the migration **Job** plus the API's
`/readyz` probe, which only passes once the schema version exists in the database.

## Repository layout

```
services/
  web/             React app, nginx config template, Dockerfile
  blog-api/        FastAPI service
    app/
      api/routes/    HTTP layer: auth, users, blogs, health
      services/      business rules (ownership checks, login) — no HTTP here
      repositories/  all SQL lives here
      core/          config (env vars), security (bcrypt, JWT)
      models.py      ORM mapping of the schema
      schemas.py     request/response models (never expose password hashes)
    tests/
  db-migrations/   the schema service: Alembic migrations + wait-for-db entrypoint
deploy/k8s/
  base/            Deployments, StatefulSet, Job, Services, NetworkPolicy, PDB
  overlays/local/  kind: namespace, dev secrets, image tags, NodePort
  kind-config.yaml
scripts/smoke-test.sh   end-to-end check used locally and in CI
compose.yaml            local stack
Makefile                `make help` lists everything
```

## Run it

### Docker Compose

```bash
cp .env.example .env     # optional; every value has a dev default
make up                  # docker compose up -d --build
```

Open **http://localhost:8080**. Interactive API docs (Swagger) are at **http://localhost:8080/api/docs**.

```bash
make smoke    # end-to-end check through nginx → API → MySQL
make logs
make down     # keep data      |  make reset  # also delete the DB volume
```

### Kubernetes (kind)

Requires [kind](https://kind.sigs.k8s.io/) and `kubectl`.

```bash
make k8s-up      # create cluster, build + load images, deploy, wait for rollout
make k8s-smoke
make k8s-status
make k8s-down
```

Open **http://localhost:30080**.

What gets deployed (namespace `blogspot`):

| Object | Why |
|---|---|
| `StatefulSet/mysql` + PVC | stable identity and storage that survives pod restarts |
| `Job/db-migrations` | the schema service; waits for MySQL, migrates, completes |
| `Deployment/blog-api` | stateless API with liveness/readiness probes, read-only root FS, non-root |
| `Deployment/web` | nginx serving the SPA and proxying `/api` |
| `ConfigMap` + generated `Secret`s | config via env; hashed secret names roll pods when values change |
| `NetworkPolicy` | only `blog-api` and `db-migrations` may reach MySQL |
| `PodDisruptionBudget` | keeps an API pod up during node drains |

### Without Docker (for development)

```bash
# API (expects MySQL; or set DATABASE_URL=sqlite:///./dev.db and run the migrations against it)
cd services/db-migrations && pip install -r requirements.txt && DB_USER=... DB_PASSWORD=... DB_NAME=blogspot ./entrypoint.sh
cd services/blog-api && pip install -r requirements-dev.txt && JWT_SECRET=$(python -c "import secrets;print(secrets.token_urlsafe(48))") uvicorn app.main:app --reload

# Frontend: the CRA dev server proxies /api to localhost:8000
cd services/web && npm install && npm start
```

## API

All routes are under `/api`. Endpoints marked 🔒 need `Authorization: Bearer <token>`.

| Method | Path | |
|---|---|---|
| POST | `/api/auth/register` | create account → 201, 409 if username/email taken |
| POST | `/api/auth/login` | → `{access_token, token_type, user}` |
| GET | `/api/users/me` 🔒 | current user |
| PATCH | `/api/users/me/avatar` 🔒 | `{ "avatar": 1-5 }` |
| GET | `/api/blogs?limit=&offset=` | newest first, with author |
| GET | `/api/blogs/{id}` | |
| POST | `/api/blogs` 🔒 | `{title, body}`; author comes from the token |
| DELETE | `/api/blogs/{id}` 🔒 | author only → 204, otherwise 403 |
| GET | `/healthz`, `/readyz` | liveness / readiness (DB reachable + schema migrated) |

## Schema changes

The schema is owned by `services/db-migrations`. To change it:

```bash
cd services/db-migrations
alembic revision -m "add tags to blogs"     # write upgrade()/downgrade() by hand
make migrate                                 # or just `make up`: it runs on every start
```

Then update `blog-api/app/models.py` to match. CI runs the API test-suite against a MySQL migrated by this service, so a mismatch fails the build.

## Testing & CI

| | |
|---|---|
| `make test-api` | ruff lint + 19 pytest tests (SQLite by default) |
| `make test-web` | React tests + production build (warnings fail) |
| GitHub Actions | migrations up → down → up on MySQL 8.4; API tests against that migrated MySQL; frontend build; **full stack in docker compose**; **full stack on a kind cluster**; images pushed to GHCR on `main` |

## From v1 to v2

| | v1 (`main`) | v2 |
|---|---|---|
| Backend | one `server.js` | FastAPI service in layers: routes → services → repositories |
| Schema | created by hand from README screenshots | versioned Alembic migrations in their own service |
| Auth | the "token" was the string `'token'`; any client could delete any blog or change any avatar | bcrypt + JWT; the server derives the user from the token and checks ownership |
| Data exposure | `GET /login/:username` returned the password hash to anyone | password hashes never leave the API |
| DB access | single connection; `throw err` in callbacks crashed the process | connection pool with pre-ping; errors become HTTP responses |
| Config | credentials and `localhost:8000` hardcoded (9 places) | environment variables; frontend calls relative `/api` |
| Frontend | logged out on refresh; pages crashed when logged out | session restored from token; protected routes |
| Repo | ~38,600 `node_modules` files committed (inside `public/`) | dependencies installed at build time |
| Running it | manual MySQL setup + two terminals | `make up` or `make k8s-up` |
| Quality gates | none | lint, unit tests, migration round-trip, compose + Kubernetes end-to-end in CI |

## Roadmap

- **AWS**: images to ECR, run on EKS (or ECS), replace the MySQL StatefulSet with RDS, secrets from Secrets Manager, all provisioned with Terraform; add an `overlays/aws`.
- **More services**: split `auth`/`users` out of `blog-api`; add a read-optimised blog feed when traffic warrants it.
- **Traffic**: Gateway API (or the AWS Load Balancer Controller on EKS) in front of `web`.
- **Ops**: structured JSON logs, Prometheus metrics + Grafana, HorizontalPodAutoscaler.
- **Frontend**: move from Create React App (unmaintained) to Vite.
