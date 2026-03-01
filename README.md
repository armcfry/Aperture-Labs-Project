# Aperture Labs - FOD Detection

CSCI 577A Spring 2026 Group Project

Foreign Object Debris (FOD) detection using Vision Language Models.

## Getting Started

### Backend Setup

#### 1. Install Ollama

Download from https://ollama.com

#### 2. Pull the model and start server

```bash
ollama pull qwen2.5vl:7b
ollama serve
```

#### 3. Setup backend (first time only)

```bash
cd backend
setup.bat
```

#### 4. Run the server

```bash
cd backend
run.bat
```

### Frontend Setup

#### 1. Install Node.js

Ensure you have Node.js 22.13.0 (LTS). Use nvm to install or switch versions; run `nvm use` from the frontend directory.

#### 2. Install packages

```bash
cd frontend
npm install
```

#### 3. Run the development server
```bash
npm run dev
```

Open [http://localhost:3998](http://localhost:3998) with your browser to see the result.

See [frontend/README.md](frontend/README.md) for more details.

## API

Can use Swagger UI: http://localhost:8000/docs

## Spin Up Databases and Run API Server

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.12 or 3.13 (3.14 may cause dependency issues with some packages)
- `pip` and `venv`

---

## 1. Environment Setup

Copy the example environment file and fill in your values:

```bash
cp backend/.env.example backend/.env
```

Your `backend/.env` should contain:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/appdb
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_DESIGNS=fod-designs
MINIO_BUCKET_IMAGES=fod-images
MINIO_USE_SSL=false
DETECTION_WEBHOOK_SECRET=your-webhook-secret-here
```

---

## 2. Start Docker Services

From the project root, start Postgres and MinIO:

```bash
docker compose up -d
```

To verify both containers are running:

```bash
docker ps
```

You should see two containers — one for `postgres` and one for `minio`.

To watch the initialization logs and confirm the schema and seed data loaded correctly:

```bash
docker logs aperture-labs-project-postgres-1 --follow
```

You should see references to `schema.sql` and `seed.sql` being processed with no errors. Press `Ctrl+C` to stop following logs.

---

## 3. Start the API

From the `backend/` directory with your virtual environment active:

```bash
uvicorn main:app --reload
```

The API will be available at:

- **API:** `http://127.0.0.1:8000`
- **Swagger docs:** `http://127.0.0.1:8000/docs`
- **MinIO console:** `http://localhost:9001` (login: `minioadmin` / `minioadmin`)