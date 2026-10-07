# Agent notes

## Base44 dev environment (`docker-compose.base44.yml`)
- Single origin: Vite dev server (bun) on host port 3000 proxies `/api` to the backend (`API_PROXY_TARGET` in `frontend/vite.config.ts`, only active when set). `VITE_API_URL` is overridden to the public 3000 URL, beating `frontend/.env`'s `localhost:8000`.
- Backend runs from source with `fastapi dev` (auto-reload) in a plain uv/python 3.14 image; venv lives in the `backend-venv` volume (`UV_PROJECT_ENVIRONMENT=/venv`).
- `prestart` one-shot service runs `uv sync`, alembic migrations and seeds the superuser before `backend` starts. After changing `uv.lock`, re-run `prestart`/restart `backend`; after changing `bun.lock`, restart `frontend`.
- Settings are read from the repo-root `.env` (the backend loads `../.env`); compose overrides `DATABASE_URL`, SMTP (Mailpit, UI on port 8025) and `FRONTEND_HOST`.
- The "Frontend directory ... does not exist" backend warning is expected: the built SPA is only produced for production images.
- Default login: `admin@example.com` / `changethis` (from `.env`; "changethis" only warns because `FASTAPI_ENV=development`).

## Verify
- `curl localhost:3000/api/v1/utils/health-check/` → `true`
- `curl -X POST localhost:3000/api/v1/login/access-token -d 'username=admin@example.com&password=changethis'` returns a token.
- Backend tests: `docker compose -f docker-compose.base44.yml exec backend sh -c 'cd backend && uv run --no-sync pytest'` (uses the dev DB). Warning: the session fixture deletes all items and users at teardown. Prefer a separate migrated database, setting `DATABASE_URL` for both Alembic and pytest.
- Item priority migration backfills existing rows to `medium`; the database keeps a server default and a check constraint. API update defaults are excluded when omitted, so title-only edits preserve priority.
