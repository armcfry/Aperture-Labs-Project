.PHONY: dev dev-down dev-reset run test test-unit test-api test-down clean

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
run:
	@chmod +x run.sh
	./run.sh

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

test-unit:
	cd backend && pytest -m unit

# test-api: test-up
# 	cd backend && pytest -m api
# 	$(MAKE) test-down

# test-e2e: dev test-up
# 	cd backend && pytest -m e2e
# 	$(MAKE) test-down