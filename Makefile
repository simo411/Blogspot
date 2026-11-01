# Blogspot v2 — common commands. Run `make help` for the list.
SHELL := /bin/bash
.DEFAULT_GOAL := help

KIND_CLUSTER := blogspot
K8S_NS       := blogspot
OVERLAY      := deploy/k8s/overlays/local
IMAGES       := db-migrations blog-api web

##@ Docker Compose
up: ## Build and start the whole stack (http://localhost:8080)
	docker compose up -d --build
	@echo "→ http://localhost:8080   (API docs: http://localhost:8080/api/docs)"

down: ## Stop the stack (keeps the database volume)
	docker compose down

reset: ## Stop the stack AND delete the database volume
	docker compose down -v

logs: ## Follow logs of all services
	docker compose logs -f

migrate: ## Re-run the schema service (applies pending migrations)
	docker compose run --rm db-migrations

smoke: ## End-to-end check against the compose stack
	./scripts/smoke-test.sh http://localhost:8080

##@ Tests (no Docker needed; API tests use SQLite)
test: test-api test-web ## Run all unit tests

test-api: ## FastAPI tests + lint
	cd services/blog-api && pip install -q -r requirements-dev.txt && ruff check . && ruff format --check . && pytest

test-web: ## React tests + production build
	cd services/web && npm ci --no-audit --no-fund && CI=true npm test -- --watchAll=false && CI=true npm run build

##@ Kubernetes (kind)
# k8s-up deletes the previous db-migrations Job first: Job specs are immutable,
# and re-running migrations is safe (Alembic skips what is already applied).
k8s-up: ## Create kind cluster, build+load images, deploy (http://localhost:30080)
	@kind get clusters | grep -qx $(KIND_CLUSTER) || kind create cluster --config deploy/k8s/kind-config.yaml
	@for img in $(IMAGES); do \
	  docker build -t blogspot/$$img:dev services/$$img && kind load docker-image blogspot/$$img:dev --name $(KIND_CLUSTER); \
	done
	-kubectl -n $(K8S_NS) delete job db-migrations --ignore-not-found
	kubectl apply -k $(OVERLAY)
	kubectl -n $(K8S_NS) rollout status statefulset/mysql --timeout=300s
	kubectl -n $(K8S_NS) wait --for=condition=complete job/db-migrations --timeout=300s
	kubectl -n $(K8S_NS) rollout restart deployment/blog-api deployment/web
	kubectl -n $(K8S_NS) rollout status deployment/blog-api --timeout=180s
	kubectl -n $(K8S_NS) rollout status deployment/web --timeout=180s
	@echo "→ http://localhost:30080"

k8s-status: ## Show pods, jobs and services
	kubectl -n $(K8S_NS) get pods,jobs,svc,pvc

k8s-smoke: ## End-to-end check against the kind cluster
	./scripts/smoke-test.sh http://localhost:30080

k8s-down: ## Delete the kind cluster
	kind delete cluster --name $(KIND_CLUSTER)

##@ Help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2} /^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)}' $(MAKEFILE_LIST)

.PHONY: up down reset logs migrate smoke test test-api test-web k8s-up k8s-status k8s-smoke k8s-down help
