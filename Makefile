.PHONY: dev dev-down dev-reset run kill kill-reset test test-unit test-api test-down test-frontend clean

# -------------------------
# OS Detection
# -------------------------
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := Unix
endif

# -------------------------
# Development
# -------------------------

dev:
	docker compose up -d

dev-down:
	docker compose down

dev-reset:
	docker compose down -v
	docker compose up -d

# Run full app locally (Docker + backend + frontend). Requires: Docker, Python 3.12+, Node.js
ifeq ($(DETECTED_OS),Windows)
run:
	.\run.bat
else
run:
	@chmod +x run.sh
	./run.sh
endif

# Stop everything: backend (8000), frontend (3998), Ollama (11434), Docker (Postgres + MinIO)
ifeq ($(DETECTED_OS),Windows)
kill:
	.\kill.bat

kill-reset:
	.\kill.bat -reset
else
kill:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null; true
	@lsof -ti :3998 | xargs kill -9 2>/dev/null; true
	@lsof -ti :11434 | xargs kill -9 2>/dev/null; true
	docker compose down
	@echo "Stopped app, Ollama, and Docker."

kill-reset:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null; true
	@lsof -ti :3998 | xargs kill -9 2>/dev/null; true
	@lsof -ti :11434 | xargs kill -9 2>/dev/null; true
	docker compose down -v
	@echo "Stopped everything and removed volumes (DB reset)."
endif

# -------------------------
# Testing
# -------------------------

# test-up:
# 	docker compose -f docker-compose-test.yml up -d
# 	@echo "Waiting for test database to be ready..."
# 	@sleep 3

# test-down:
# 	docker compose -f docker-compose-test.yml down

test:
	cd backend && pytest

test-backend:
	cd backend && pytest -m unit

test-frontend:
	cd frontend && npm test

# test-api: test-up
# 	cd backend && pytest -m api
# 	$(MAKE) test-down

# test-e2e: dev test-up
# 	cd backend && pytest -m e2e
# 	$(MAKE) test-down