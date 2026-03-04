# Aperture Labs - FOD Detection

CSCI 577A Spring 2026 Group Project

Foreign Object Debris (FOD) detection using Vision Language Models.

---

## Run the app locally (one command)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/), Python 3.12 or 3.13, Node.js (e.g. 22.x), `pip`, `npm`.

From the project root:

```bash
make run
```

Or directly:

```bash
chmod +x run.sh && ./run.sh
```

This will:

1. Start Postgres and MinIO with `docker compose up -d`
2. Create `backend/.env` from defaults if missing (ports 5434, 9002)
3. Create a Python venv and install backend deps, then start the API at **http://127.0.0.1:8000**
4. Run `npm install` if needed and start the frontend at **http://localhost:3998**

**Log in:** `test@example.com` / `test`

Press **Ctrl+C** to stop the backend and frontend; Docker keeps running. To stop Docker: `make dev-down` or `docker compose down`.

**If `make run` or `./run.sh` fails** (e.g. on Windows, or a step errors), use the [step-by-step instructions](#step-by-step-if-one-command-doesnt-work) below.

---

## Optional: Ollama (real VLM detection)

For live FOD detection instead of mock results:

1. Install [Ollama](https://ollama.com)
2. Run: `ollama pull qwen2.5vl:7b` then `ollama serve`

---

## Step-by-step (if one command doesn't work)

Use these steps if `make run` fails or you're on Windows (where `run.sh` is not supported). Run each step in order; use **two terminals** for backend and frontend.

### 1. Environment

Ensure `backend/.env` exists. If not, copy from example or create with:

```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@127.0.0.1:5434/appdb
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINIO_ENDPOINT=localhost:9002
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_DESIGNS=designs
MINIO_BUCKET_IMAGES=images
MINIO_USE_SSL=false
DETECTION_WEBHOOK_SECRET=dev-webhook-secret
```

(Ports 5434 and 9002 match `docker-compose.yml`.)

### 2. Docker

From the project root, start Postgres and MinIO:

```bash
docker compose up -d
```

Optional: wait a few seconds, then check containers are up: `docker ps`.

### 3. Backend

In a **first terminal**, from the project root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Leave this terminal running. Then check:

- API: http://127.0.0.1:8000  
- Swagger: http://127.0.0.1:8000/docs  

### 4. Frontend (second terminal)

Open a **new terminal**, from the project root:

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:3998  
- Log in with: `test@example.com` / `test`  

---

## Code quality

SonarQube: https://sonarcloud.io/project/overview?id=Aperture-Labs-SP-26_Aperture-Labs-Project

---

## Running tests

From the project root:

```bash
make test        # full suite
make test-unit   # unit tests only
```

Or from `backend/` with venv active:

```bash
pytest
pytest tests/unit/services/test_auth_service.py -v
```

---

## Teardown

- Stop backend/frontend: Ctrl+C (if you used `./run.sh`).
- Stop Docker: `make dev-down` or `docker compose down`.
- Reset DB and storage: `docker compose down -v` then `docker compose up -d`.

---

## Frontend details

See [frontend/README.md](frontend/README.md) for scripts, env (`NEXT_PUBLIC_API_URL`), and port (3998).
