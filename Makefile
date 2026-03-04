.PHONY: dev dev-down test test-unit test-api test-down clean

# -------------------------
# Development
# -------------------------

dev:
	docker compose up -d

dev-down:
	docker compose down

dev-reset:
	docker compose down
	docker volume rm aperture-labs-project_postgres_data aperture-labs-project_minio_data || true
	docker compose up -d

# -------------------------
# Testing
# -------------------------

test-up:
	docker compose -f docker-compose-test.yml up -d
	@echo "Waiting for test database to be ready..."
	@sleep 3

test-down:
	docker compose -f docker-compose-test.yml down

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