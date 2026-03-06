# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FOD (Foreign Object Debris) detection system using Vision Language Models. A full-stack application with a FastAPI backend and Next.js frontend that allows users to upload product images for AI-powered anomaly detection.

## Build & Run Commands

### Full Stack (Docker + Backend + Frontend)
```bash
make run          # Start everything (Docker, backend, frontend, optionally Ollama)
make kill         # Stop all services
make kill-reset   # Stop all and reset database volumes
```

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Only
```bash
cd frontend
npm install
npm run dev              # Port 3998
npm run dev:turbopack    # With Turbopack
npm run lint             # ESLint
npm run lint -- --fix    # Auto-fix lint issues
```

### Docker Services
```bash
docker compose up -d     # Start Postgres (5434) and MinIO (9002)
docker compose down      # Stop services
docker compose down -v   # Stop and reset volumes
```

## Testing

```bash
# From project root
make test          # Run all pytest tests
make test-unit     # Run unit tests only

# From backend directory with venv active
pytest
pytest tests/unit/services/test_auth_service.py -v  # Single test file
pytest -m unit     # Only unit-marked tests
```

Coverage reports auto-generate to `backend/code_coverage/`.

## Architecture

### Backend (FastAPI)
- `main.py` - App entry point, router registration, middleware, exception handlers
- `routers/` - API endpoints (auth, projects, submissions, anomalies, detection, storage, users)
- `services/` - Business logic layer (each router has corresponding service)
- `schemas/` - Pydantic request/response models
- `models/ollama_vlm.py` - Vision Language Model integration with Ollama
- `core/` - Config (pydantic-settings), custom exceptions, exception handlers
- `db/` - SQL schema, seed data, init scripts for Postgres

### Frontend (Next.js 15 + React 19)
- `src/app/` - App Router pages (login, projects, inspect)
- `src/components/` - Reusable UI (Header, Sidebar, InspectHistorySidebar, DesignSpecPreview)
- `src/components/ui/` - shadcn/ui primitives
- `src/lib/api.ts` - All backend API calls (typed fetch wrappers)
- `src/hooks/` - Custom React hooks
- `src/app/AppProvider.tsx` - Global state context (theme, user, currentProject, sidebar)

### Data Flow
1. User selects project → uploads product image via `/storage/image`
2. Frontend calls `/detect` with image + project_id
3. Backend loads project design specs from MinIO, builds VLM prompt
4. Ollama (qwen2.5vl:7b) analyzes image for defects
5. Results stored as submissions + anomalies in Postgres
6. Frontend displays pass/fail with defect list

### Database Schema
- `users` - Authentication
- `projects` - Inspection projects with design specs
- `project_members` - User-project associations (owner/editor/viewer roles)
- `submissions` - Image inspection records (status: queued/running/complete/failed)
- `anomalies` - Detected defects linked to submissions (severity: low/med/high)

### Storage (MinIO)
- `designs` bucket - Project design spec PDFs
- `images` bucket - Uploaded product images for inspection

## Environment

Backend requires `.env` in `backend/` with:
- `DATABASE_URL` - Postgres connection (default: localhost:5434)
- `MINIO_*` - MinIO connection settings (endpoint, keys, buckets)
- `DETECTION_WEBHOOK_SECRET` - Webhook auth

Frontend uses `NEXT_PUBLIC_API_URL` (default: http://localhost:8000)

## Test Credentials

- `test@example.com` / `test`
- `alice@example.com`, `bob@example.com`, `carol@example.com` / `password123`
