# TradeAfric MVP v2 — Full Stack

Django REST backend + Next.js frontend implementing the core MVP trade flow:
register → KYC → RFQ → Offer → negotiation → accept (auto-issues Purchase Order) →
logistics (job pool → claim → track) → quality inspection (job pool → claim →
report) → documents → notifications, with a dedicated dashboard for each role
(buyer, seller, logistics partner, inspector, admin).

**Start here:** [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) — maps the original
PRD to what's actually built, module by module, with known gaps, bugs already
found and fixed, and prioritized next steps. Read that before making changes.

```
tradeafric/
├── backend/              Django + DRF API (see backend/README.md)
├── frontend/              Next.js app, proxies /api & /media to backend (see frontend/README.md)
├── docker-compose.yml     Postgres + backend (gunicorn) + frontend + Caddy (auto HTTPS)
├── Caddyfile
├── PROJECT_STATUS.md       ← PRD-to-implementation map, read this first
├── tradeafric_mvp_plan.md          original architecture/scope planning doc
└── tradeafric_django_setup_guide.md   original Django setup reasoning doc
```

## Running locally (no Docker)

**Terminal 1 — backend:**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://localhost:8000
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local          # BACKEND_INTERNAL_URL, defaults to localhost:8000
npm run dev                          # http://localhost:3000
```

Visit **http://localhost:3000** — always go through the frontend's own origin,
not the Django port directly, since auth cookies rely on the same-origin proxy
(see PROJECT_STATUS.md §7 for why this matters).

Register a buyer and a seller (separate browser sessions or incognito), approve
their KYC via Django admin at http://localhost:8000/admin/ or via an
admin-role account through `/admin/kyc-review`, then run a full RFQ → Offer →
Purchase Order → Logistics → Inspection flow. Register a `logistics` and
`inspector` role account too, to see their dedicated dashboards.

## Running via Docker (production-shaped)

```bash
cp .env.example .env      # fill in real secrets — see comments in the file
docker compose up --build
```
Caddy will request a real Let's Encrypt certificate if `DOMAIN` is a real,
DNS-pointed domain, or serve local HTTPS if left as `localhost`.

## Deploying to Render

`render.yaml` deploys the whole stack (Postgres + backend + frontend) in one
Blueprint — see [`RENDER_DEPLOY.md`](./RENDER_DEPLOY.md) for the full walkthrough.
Short version: push to GitHub, **New → Blueprint** in the Render dashboard, done.

## Status (as of `v2.0.0-mvp` on both repos)

- **Backend:** 28 automated tests passing (`pytest`). Full 15-step trade flow
  (registration → KYC → RFQ → offer → accept → PO → logistics claim/track →
  inspection claim/report → order status transition) verified live through the
  actual Next.js proxy — not just against the backend directly.
- **Frontend:** `next build` and `eslint` both clean (0 errors).
- **Deployment:** Dockerfiles, `docker-compose.yml`, and `Caddyfile` written and
  cross-checked; gunicorn was booted directly against production settings
  (outside Docker, since this environment has no Docker daemon) and confirmed
  serving requests with correctly-configured httpOnly cookies and whitenoise
  static files.
- **A critical bug was found and fixed this session:** an infinite redirect
  loop between the frontend proxy and Django's trailing-slash handling, which
  only surfaced once the stack was tested through the real proxy rather than
  hitting the backend directly. Full writeup in `PROJECT_STATUS.md` §6 — worth
  reading before assuming "it works" from backend tests alone.

## Next steps

See `PROJECT_STATUS.md` §9 for the prioritized list. Short version: Ratings &
Reputation (planned for MVP, never built), Playwright end-to-end tests, a CI
pipeline, then real GPS for logistics and a proper Dispute model. 
