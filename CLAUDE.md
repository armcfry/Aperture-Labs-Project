# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

### Full Stack
```bash
make run          # Start Docker + backend + frontend
make kill         # Stop all services
make kill-reset   # Stop all and wipe database volumes (required after schema changes)
```

### Backend Only
```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Only
```bash
cd frontend
npm run dev              # http://localhost:3998
npm run lint:fix         # ESLint auto-fix
npm run prettier:fix     # Prettier auto-fix
```

### Testing
```bash
# Backend (from project root)
make test                # All pytest tests with coverage
make test-unit           # Unit tests only

# Backend (from backend/ with venv active)
pytest tests/unit/services/test_auth_service.py -v   # Single file
pytest -k "test_login"                               # Single test by name

# Frontend (from frontend/)
npm test                                             # All vitest tests
npx vitest run src/__tests__/login.test.tsx          # Single file
```

Backend coverage reports output to `backend/htmlcov/`. Frontend coverage (lcov) outputs to `frontend/coverage/`.

## Architecture

### Detection Pipeline (the critical flow)

Image upload triggers async FOD detection in a background thread — **not** a synchronous API call:

1. `POST /storage/image` — stores image in MinIO, creates a `queued` Submission row, spawns a background thread
2. `detection_service._run_detection()` — loads image + PDF specs from MinIO, calls Ollama VLM (`qwen2.5vl:7b`), runs OWLv2 for bounding boxes on any detected defects, writes results to DB
3. Frontend polls `GET /projects/{id}/submissions` every 3s via `useInspectionHistory` hook while any submission is `queued`/`running`
4. Status transitions fire toast notifications via `InspectHistorySidebar.handleStatusChange`

`POST /detect` is a **legacy synchronous endpoint** still in the codebase (`routers/detection.py`) but is no longer called by the main frontend flow. Do not confuse it with the active pipeline.

### Backend (FastAPI, `backend/`)
- `main.py` — router registration, CORS, exception handlers
- `routers/` — thin HTTP layer; each router delegates entirely to its matching service
- `services/detection_service.py` — the async detection pipeline (OWLv2 + VLM)
- `models/ollama_vlm.py` — Ollama VLM integration; builds prompts from PDF spec text
- `models/owlv2.py` — zero-shot bounding box annotation using `google/owlv2-base-patch16-ensemble`; lazy-loaded on first use (~600 MB download)
- `schemas/enums.py` — canonical status values: `queued | running | complete | failed | error | timeout`
- `db/schema.sql` — source of truth for DB schema; `init.sql` runs this + `seed.sql` on container start

### Frontend (Next.js 15 + React 19, `frontend/src/`)
- `app/AppProvider.tsx` — global context: `user`, `currentProject`, `theme`, `hasRestoredFromStorage`
- `app/ClientRoot.tsx` — wraps the tree with `AppProvider` + `ToastProvider`
- `lib/api.ts` — all typed fetch wrappers; `ApiSubmission` and `ApiAnomaly` are the primary backend types
- `hooks/useInspectionHistory.ts` — polls submissions API, detects status transitions, fires `onStatusChange` callback; uses `SUBMISSION_UPLOADED_EVENT` custom event for immediate refresh after upload
- `context/ToastContext.tsx` — `ToastProvider` / `useToast()`; 5s auto-dismiss with 220ms exit animation
- `lib/inspection-store.ts` — **legacy** local-storage store for old pre-API inspection data; still used by the result page for non-`api-` prefixed IDs

### Database
Each project's MinIO bucket is named by its UUID (e.g. `aaaaaaaa-...`), with `designs/` prefix for PDFs and `images/` prefix for uploaded photos. There is no shared `designs` or `images` bucket.

Submissions table key columns: `status`, `pass_fail`, `anomaly_count`, `error_message`, `annotated_image` (base64 PNG from OWLv2, nullable).

**After any change to `schema.sql` or `seed.sql`, run `make kill-reset && make run` to rebuild the DB.**

### Passwords
Auth uses plain-text password comparison (`utils/password.py`). No hashing. Test credentials:
- `test@example.com` / `test`
- `alice@example.com`, `bob@example.com`, `carol@example.com` / `password123`

### Frontend Tests
Tests live in `frontend/src/__tests__/`. Each test file is annotated with the requirements it covers. The `useInspectionHistory` tests use `vi.useFakeTimers()` + `vi.runAllTimersAsync()` to advance the polling loop. `InspectHistorySidebar` tests capture the `onStatusChange` callback via a module-level variable in the mock.
