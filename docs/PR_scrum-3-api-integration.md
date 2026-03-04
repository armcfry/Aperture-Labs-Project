# Pull Request: Scrum 3 – API Integration, Auth Persistence, Inspection History

## Summary

Wires the frontend to the backend API, persists login across reloads, and improves inspection history with running placeholders and progress. Adds synchronous FOD detection (`POST /detect`), startup seed data (demo project + optional VLM run), and shared UI for design specs and inspection history.

---

## What changed

**Backend**
- **New:** `routers/detect.py` — `POST /detect` for image upload; Ollama VLM (default `qwen2.5vl:7b`), mock when Ollama unavailable. `seed_data.py` — creates buckets, demo project, uploads design + sample image, optional VLM run on startup. `services/severity_mapping.py` — maps VLM severity to API severity.
- **Updated:** `main.py` (detect router, lifespan seed, CORS), auth/storage/projects/members/submissions/anomalies routers and services, schemas, DB seed/schema, exception handlers, unit tests.

**Frontend**
- **Auth:** User persisted in localStorage; `hasRestoredFromStorage` so protected routes only redirect after restore (fixes reload sending user to login).
- **Inspection history:** Placeholder with “ANALYZING” + progress bar; merge fix on API error; pre-fill from local store. Store: `saveInspectionPlaceholder`, `updateInspectionProgress`, `updateInspectionWithResult`; event-driven sidebar updates.
- **API client:** Login, projects, storage (designs/images), submissions, anomalies, `detectFod` → `POST /detect`.
- **Pages:** Login, Projects (list/create/design specs/archive), Inspect (multi-photo upload, run analysis, history), Inspect result (batch view, defects, design preview).
- **New components:** DesignSpecLink, DesignSpecPreview, InspectionHistoryList, alert, loading-spinner. Hook: `useInspectionHistory(projectId)`.

**Docs / run locally**
- **README** — Rewritten: “Run the app locally (one command)” first (`make run` or `./run.sh`), then step-by-step fallback if it fails or on Windows. Env snippet uses ports 5434, 9002.
- **run.sh** (new) — Single script: `docker compose up -d`, create `backend/.env` if missing, start backend (venv + uvicorn) and frontend (npm run dev). Ctrl+C stops backend/frontend; Docker keeps running.
- **Makefile** — `make run` runs `./run.sh`; `dev-reset` simplified to `down -v` then `up -d`.

---

## How to test

**Run the app:** From repo root, `make run` (or see README step-by-step). Log in with **test@example.com** / **test**.

**Quick checks**
1. **Login** → lands on Projects; **reload** → stay on same page (no redirect to login).
2. **Projects** → create project, upload design spec (PDF), open/preview.
3. **New Inspection** → upload photos, **Start Analysis** → History shows new card with “ANALYZING” and progress bar; when done, PASS/FAIL and Report.
4. **Inspect result** → click item in History → batch result and defect list.
5. **Logout** → redirect to login; reload stays on login.
6. **API:** Swagger at http://127.0.0.1:8000/docs — try `POST /auth/login`, `GET /projects`, `POST /detect` (image file).
7. **Tests:** `make test` from root.

---

## Files

52+ files changed. **New:** `run.sh`, `backend/routers/detect.py`, `backend/seed_data.py`, `backend/services/severity_mapping.py`; `frontend/hooks/useInspectionHistory.ts`, DesignSpecLink, DesignSpecPreview, InspectionHistoryList, alert, loading-spinner, icon. **Updated:** README, Makefile; backend routers/services/schemas/db/tests; frontend app/components/lib.

---

## Notes

- Demo user: **test@example.com** / **test** (from `seed.sql`).
- Ollama optional; without it `/detect` returns mock result.
- Ports: backend 8000, frontend 3998, Postgres 5434, MinIO 9002/9001.
