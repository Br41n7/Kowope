# Deploying to Render

This repo includes `render.yaml`, a [Render Blueprint](https://render.com/docs/blueprint-spec)
that provisions the entire stack in one pass: Postgres, the Django/gunicorn
backend, and the Next.js frontend, fully wired together.

## One-time setup

1. Push this repo to GitHub (Render Blueprints deploy from a git repo, not a local zip).
2. In the Render dashboard: **New → Blueprint**, point it at the repo, Render reads `render.yaml` automatically.
3. Render will provision, in order: the `tradeafric-db` Postgres instance, then `tradeafric-backend`, then `tradeafric-frontend` (it waits on the `fromService`/`fromDatabase` references automatically).
4. First deploy only — create a Django superuser so you can reach `/admin/`:
   - Render dashboard → `tradeafric-backend` → **Shell** tab → run `python manage.py createsuperuser`

That's it — no manual env var entry needed. `render.yaml` wires `DATABASE_URL`, `ALLOWED_HOSTS`, `SECRET_KEY` (auto-generated), and `BACKEND_INTERNAL_URL` (the frontend→backend proxy target) automatically via Render's `fromDatabase`/`fromService`/`generateValue` mechanisms.

## What each service does

| Service | Runtime | Notes |
|---|---|---|
| `tradeafric-db` | Postgres | `starter` plan by default — swap to `free` for a throwaway test (expires after 30 days) |
| `tradeafric-backend` | Docker (`backend/Dockerfile`) | gunicorn, `/healthz` health check, 1GB persistent disk mounted at `/app/media` |
| `tradeafric-frontend` | Docker (`frontend/Dockerfile`) | `next start`, proxies `/api/*` and `/media/*` to the backend's Render URL (see `frontend/next.config.ts`) |

**Always visit the app at the `tradeafric-frontend` URL, not the backend's.** Auth relies on the frontend proxying requests to the backend so cookies stay same-origin from the browser's perspective — hitting the backend directly will work for the API itself but won't share auth state with the frontend pages.

## Persistent disk — the one real limitation to know about

The backend's media disk (`/app/media`) ties that service to a **single instance** — Render disks don't support horizontal scaling. Fine for an MVP pilot; before scaling past one instance, move to S3-compatible object storage instead (flagged as a next step in `PROJECT_STATUS.md` §9 — `django-storages` is already in `requirements.txt`, commented out, ready to enable).

## Free tier notes (if you swap `plan: starter` → `plan: free` while testing)

- Free web services **spin down after ~15 minutes of inactivity** and take roughly 50 seconds to wake back up on the next request — expect a slow first load after idle periods.
- Free Postgres databases **expire and are deleted after 30 days** — don't use `free` for anything you want to keep.
- Free services **cannot have a persistent disk attached** — if you drop the backend to `free`, remove the `disk:` block from `render.yaml` first, or the deploy will fail. Uploaded files would then be lost on every restart/redeploy.

## Verifying the deploy

```bash
curl https://tradeafric-backend.onrender.com/healthz
# {"status": "ok", "database": true}
```
Then visit `https://tradeafric-frontend.onrender.com`, register a buyer and seller, and run through the trade flow as in local testing — this exercises the same proxy path that was verified locally (see `PROJECT_STATUS.md` §6, the trailing-slash bug writeup) and is the actual configuration Render will run.

## If you'd rather not use the Blueprint

Everything in `render.yaml` can be set up manually through the Render dashboard instead — create the Postgres database first, then each web service (Docker runtime, pointing at the respective `Dockerfile`), and copy the `envVars` from `render.yaml` into each service's Environment tab by hand. The Blueprint just automates exactly that.
