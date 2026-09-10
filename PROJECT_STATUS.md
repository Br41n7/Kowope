# TradeAfric — Project Status & Handoff Document

**Purpose of this document:** map the original PRD (from Trade Afric Resources & Investment Ltd, 28 Aug 2026) to what's actually built, module by module, so any developer or team can pick this up without re-deriving context. Written at the point where MVP v2 is feature-complete and verified end-to-end.

**Last updated:** this session. **Current tag:** `v2.0.0-mvp` on both `backend` and `frontend` repos.

---

## 1. What the PRD actually asked for

The original PRD describes a **Digital Trade Infrastructure Platform**, not a simple marketplace — it explicitly frames itself as five interconnected marketplaces sharing one identity/wallet/document system:

1. **Commodity Marketplace** — RFQs, offers, negotiation, contracting, logistics, quality assurance, insurance, settlement
2. **Trade Finance Marketplace** — PO finance, invoice finance, factoring, receivables finance, inventory finance, syndicated funding
3. **Trade Services Marketplace** — logistics, inspection, insurers, customs brokers, freight forwarders, warehousing, legal
4. **Financial Services Marketplace** — escrow, bank guarantees, FX, treasury, wallets, payments, working capital
5. **Market Intelligence Marketplace** — prices, analytics, forecasts, benchmarking, premium research

The PRD lists 30 numbered modules (Module 1–30, skipping 29) covering everything from KYC to an AI credit/risk scoring engine to a full API/integration hub.

**The realistic read on this PRD**, given as direct feedback early in this engagement and still true: this describes 3–4 separate regulated businesses (a commodity marketplace + a fintech/BaaS product + an insurance broker + a data/analytics product) bolted into one vision document. It is not buildable as a single MVP, and several modules (escrow, bank guarantees, FX, wallets) are **regulated financial activities in Nigeria requiring a licensed partner (CBN-regulated bank/MFB or a BaaS provider), not something a dev team builds from scratch.**

---

## 2. MVP scope decision (what we chose to build first)

Out of the 30 PRD modules, the MVP targets the smallest slice that proves the core value proposition: **a buyer and seller can discover each other, negotiate, transact, and get the goods verified and delivered, with a document trail throughout.**

That maps to PRD Modules: **1 (User Registration/KYC), 2 (Digital Marketplace), 3 (RFQ Management), 5 (Negotiation), 6 (Digital Purchase Orders), 13 (Quality Assurance), 15 (Logistics), 20 (partial — Ratings), 22 (Document Vault)**.

Everything involving money movement (Modules 7–12, 14, 17–18), AI/scoring (26–27), and integrations (30) is **deliberately deferred** — see Section 5.

---

## 3. Module-by-module status

Legend: ✅ Done & tested · 🟡 Partial · 🚫 Deliberately deferred (not started)

| PRD Module | What it is | Status | Where it lives |
|---|---|---|---|
| 1. User Registration & KYC | Role-based onboarding (buyer/seller/logistics/inspector/admin), KYC submit + admin review | ✅ | `apps/accounts` (backend), `/register`, `/kyc`, `/admin/kyc-review` (frontend) |
| 2. Digital Marketplace | Commodity listings, RFQs, negotiation, price discovery | ✅ | `apps/marketplace`, `/buyer/rfqs`, `/seller/rfqs` |
| 3. RFQ Management | Buyer RFQ creation with full spec (grade, qty, delivery, quality/payment prefs), seller offer submission | ✅ | `apps/marketplace` (`RFQ`, `Offer` models) |
| 4. Offer Comparison Engine | Compare offers by price/delivery/quality/rating/financing | 🚫 | Not built — MVP shows offers as a flat list per RFQ; no scoring/ranking |
| 5. Negotiation Engine | Chat, counter-offers, document exchange, acceptance | 🟡 | Basic message thread + file attachments built (`NegotiationMessage`). No formal "counter-offer" object (a new price is just another message), no version history |
| 6. Digital Purchase Orders | Electronic PO generation, digital signatures, amendments | 🟡 | PO auto-generated on offer acceptance with an **immutable terms snapshot** (tested — see `core/services/offer_service.py::accept_offer`). No digital signatures. `OrderAmendment` model exists but has **no API/UI wired to it yet** — dead code, flag for next dev |
| 7. Escrow Module | Buyer deposits funds, held, released on conditions | 🚫 | Requires a licensed escrow/payments partner. Not started. `payment_pref` field exists on RFQ as a *stated preference* only — no money moves |
| 8. Bank Guarantee Module | Financier issues/verifies guarantees | 🚫 | Not started — same licensing blocker as escrow |
| 9. Trade Finance Marketplace | Financiers browse approved POs/invoices, compete to finance | 🚫 | Not started |
| 10–12. PO/Invoice Financing, Factoring | | 🚫 | Not started — all require a licensed financier network first |
| 13. Quality Assurance Module | Inspection request → assign → schedule → report → certs/photos → GPS | 🟡 | Request/assign/report/certs/photos all built and tested. **GPS fields exist on the model (`gps_lat`/`gps_lng`) but the frontend never populates them** — no browser geolocation capture wired in |
| 14. Insurance Marketplace & Claims | | 🚫 | Not started |
| 15. Logistics Marketplace | Haulage requests, quotes, GPS tracking, POD | 🟡 | Request → job-pool → claim/assign → manual status updates all built and tested. **No real GPS/live-map tracking** — status updates are manual text entries by the logistics partner, not device-reported location. No freight quoting (single implicit "job," no competing quotes) |
| 16. Supply Chain Visibility | Live tracking, map, milestones, alerts | 🚫 | Not started — would sit on top of Module 15's manual updates once real GPS exists |
| 17. Digital Wallet | Per-participant wallet, linked bank account | 🚫 | Not started — same licensing blocker |
| 18. FX Marketplace | Currency exchange, spot/forward, settlement | 🚫 | Not started |
| 19. Market Intelligence | Prices, volumes, trends, reports | 🚫 | Not started |
| 20. Ratings & Reputation | Buyer/seller/logistics/inspector ratings, dispute history | 🚫 | **Not built at all** — earlier plan doc listed this as MVP scope but it was never implemented. Genuine gap, not a deferred-on-purpose item |
| 21. Dispute Resolution | Raise dispute, arbitrator, resolution | 🟡 | `PurchaseOrder.status` includes `disputed` as a state buyers/sellers can set. **No dispute object, no evidence upload, no arbitrator workflow** — it's just a status flag today |
| 22. Document Vault | Store POs, invoices, BOLs, certs, contracts with versioning | ✅ | `apps/documents` — generic (`GenericForeignKey`) vault attachable to any model, versioned per `doc_type`, access-restricted to order participants (this was a real bug fixed and tested this session — see Section 6) |
| 23. Trade Analytics | Revenue, volumes, orders, margins, risk dashboards | 🚫 | Not started |
| 24. Administration Portal | Users, transactions, fees, approvals, compliance, audit logs | 🟡 | Django admin gives basic CRUD + KYC approval actions out of the box. **No custom audit-log model, no fee/transaction management** (there's no money to manage yet) |
| 25. Trade Verification Engine | Party/trade/commodity verification, fraud detection | 🚫 | Not started — this is a substantial ML/rules engine, out of MVP scope entirely |
| 26. Trade Confidence & Risk Scoring | Dynamic per-participant/transaction scores | 🚫 | Not started |
| 27. AI Credit & Risk Analytics | AI credit scoring, fraud detection, market risk | 🚫 | Not started — needs real transaction volume/history to even be meaningful |
| 28. Document Management System (DMS) | OCR, digital signatures, workflow, watermarking | 🟡 | Basic version-controlled storage exists (Module 22). **No OCR, no digital signatures, no workflow/approval states, no watermarking** |
| 30. API & Integration Hub | Banking/ERP/logistics/insurance/customs APIs, developer portal | 🚫 | Not started. `drf-spectacular` auto-generates OpenAPI docs at `/api/docs/`, which is the only "integration-readiness" piece that exists |

**Not in the table:** Module 29 doesn't exist in the original PRD (numbering skips from 28 to 30 in the source document — not an omission on our end).

---

## 4. What's built beyond the PRD's explicit module list

- **Role-based job-pool workflow** for logistics partners and inspectors (claim an unassigned job, get scoped visibility to your own + open jobs) — the PRD describes these roles but never specifies *how* a logistics partner or inspector actually finds and claims work. We designed and built this from scratch this session.
- **httpOnly cookie authentication** via a same-origin Next.js proxy — not in the PRD at all (an implementation-level security decision), but worth knowing: this is *why* the frontend and backend must be deployed together behind one origin (see Section 7).
- **Full Docker deployment stack** (Dockerfiles, docker-compose, Caddy for automatic HTTPS) — infrastructure, not a PRD feature, but necessary to actually ship anything.

---

## 5. Explicit non-goals for MVP (don't build these without a business decision first)

Escrow, bank guarantees, FX, wallets, financier/factoring marketplace, insurance marketplace, AI risk/credit scoring, the Trade Verification Engine — **all of these require either a licensed financial partner integration or a level of transaction history/ML investment that doesn't make sense before the core loop has real usage data.** If a future team is asked to "just add escrow," the correct first step is a conversation about which licensed provider (a Nigerian MFB, or a BaaS platform like Flutterwave/Paystack/Mono) will actually hold and move the money — building this in-house is both a regulatory and security liability.

---

## 6. Bugs found and fixed during this build (read this before touching auth or the API layer)

These aren't hypothetical — each was caught by actually running the system, not just writing code:

1. **Any authenticated user could modify any order's logistics/inspection records.** Original `LogisticsRequestViewSet`/`InspectionRequestViewSet` only checked `IsAuthenticated`. Fixed by adding role + ownership scoping (`core/permissions.py::IsLogisticsRole`/`IsInspectorRole`, plus per-action ownership checks). Covered by `apps/logistics/tests/test_logistics.py` and `apps/quality/tests/test_quality.py`.
2. **File URLs would have been absolute internal-Docker-hostnames in production** (e.g. `http://backend:8000/media/...`, unreachable from a browser). Fixed with `core/mixins.py::RelativeMediaURLMixin`, which strips `request` from serializer context so DRF's `FileField` returns relative URLs, resolved correctly by the browser against its own origin.
3. **`Document` access wasn't restricted to order participants** — anyone authenticated could list/view any order's documents. Fixed and covered by `apps/documents/tests/test_documents.py`.
4. **No `.dockerignore` existed.** `COPY . .` in the backend Dockerfile would have baked the local dev `.env` (containing a real, if low-stakes, `SECRET_KEY`) into the production image — silently defeating the fail-loud `SECRET_KEY`/`ALLOWED_HOSTS` checks in `config/settings/production.py`. This was caught by actually running gunicorn against production settings and testing the fail-loud checks, not by inspection. Fixed with `backend/.dockerignore` and `frontend/.dockerignore`.
5. **Critical: infinite redirect loop through the deployment-realistic proxy setup.** Next.js's `/api/:path*` rewrite does not preserve a trailing slash when reconstructing the destination URL. With Django's default `APPEND_SLASH=True`, this meant: POST requests hit a hard 500 (Django can't redirect a POST and keep the body), and GET requests looped forever (Django redirects to add the slash back → proxy strips it again on the next hop → forever). **This was invisible in earlier testing** because direct `curl`/Python-client tests against the Django port never went through the proxy. It only surfaced once we tested through the actual frontend origin, which is what a real browser does. Fixed by making the entire API slash-less (`DefaultRouter(trailing_slash=False)` everywhere, `APPEND_SLASH=False`, `skipTrailingSlashRedirect: true` in `next.config.ts`) and re-verified with a full 15-step cookie-jar integration test through the real proxy (see `git log` — the commit tagged around this fix has the full writeup).

**Lesson for whoever continues this:** several of these bugs only exist at the *integration* boundary (frontend↔backend, dev↔production settings, local↔Docker). Unit tests alone didn't catch any of them — they were all found by actually running the full stack together the way it will really be deployed. Keep doing that before every release.

---

## 7. Architecture reference

```
tradeafric/
├── backend/        Django 6 + DRF, cookie-based JWT auth, SQLite (dev) / Postgres (prod)
├── frontend/        Next.js 16 (App Router, TS, Tailwind v4), proxies /api & /media to backend
├── docker-compose.yml   db (Postgres) + backend (gunicorn) + frontend (next start) + caddy (TLS)
├── Caddyfile         routes /api,/admin → backend; /static,/media → files directly; else → frontend
└── .env.example       docker-compose secrets template
```

**Why the proxy matters:** the frontend and backend are NOT meant to be deployed as independent, cross-origin services. The httpOnly auth cookies only work because Next.js proxies `/api/*` to Django server-side, making the browser see everything as same-origin. If a future dev "simplifies" this by pointing the frontend directly at a separate API domain, **auth will silently break** (cookies won't be sent cross-origin without additional CORS+SameSite=None+Secure work that isn't currently configured). Keep the proxy, or explicitly redo the auth model if you need to split origins.

**Backend apps** (`apps/`): `accounts` (users, KYC, cookie auth), `marketplace` (RFQ/Offer/negotiation), `orders` (PurchaseOrder), `documents` (generic version-controlled vault), `logistics`, `quality`, `notifications`. Shared logic in `core/` (`permissions.py`, `services/` for business logic kept out of views, `mixins.py`, `authentication.py`).

**Frontend routes** (`src/app/`): `/register`, `/login`, `/kyc`, `/buyer/rfqs[/new][/[id]]`, `/seller/rfqs`, `/seller/offers`, `/orders[/[id]]`, `/logistics`, `/inspector`, `/admin/kyc-review`, `/notifications`.

**Full git history** on both repos is tagged per milestone — `git log --oneline` and `git tag` on either repo tell the real story better than prose can. Current tag: `v2.1.0-render-ready`.

### Render deployment

`render.yaml` at the project root is a [Render Blueprint](https://render.com/docs/blueprint-spec) that provisions the whole stack (Postgres + backend + frontend) in one pass — see `RENDER_DEPLOY.md` for the full walkthrough. Two things worth knowing if you touch this:

- **Media serving in production was a real, silent bug.** Django's built-in `static()` URL helper (`django.conf.urls.static.static`) no-ops whenever `DEBUG=False` — calling it unconditionally *looks* like a fix but does nothing. The actual fix wires `django.views.static.serve` directly (see `config/urls.py`). Verified by actually booting gunicorn under production settings and fetching a file over HTTP, not just by reading the code — this class of bug (something that looks correct but is quietly a no-op) doesn't show up in `manage.py check` or in tests that never run under `DEBUG=False`.
- **`ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`/`BACKEND_INTERNAL_URL` are wired via Render's `fromService`/`fromDatabase` blueprint mechanisms**, not hand-entered — see the comments in `render.yaml` for exactly how. `CSRF_TRUSTED_ORIGINS` is derived in Django settings from `ALLOWED_HOSTS` rather than needing its own env var, since they must always agree.
- The backend's media disk pins it to a single Render instance (Render disks don't support autoscaling) — acceptable for a pilot, but it's the same S3-migration item already flagged in §9 below.

---

## 8. Test coverage status

- Backend: 28 automated tests (`pytest`), covering auth/KYC, marketplace accept-offer business logic (including the immutable terms snapshot and permission checks), order status guards, logistics/inspection role-gating and job-pool mechanics, document access control.
- Frontend: `next build` + `eslint` both clean (0 errors, 3 pre-existing stylistic warnings about `useEffect` dependencies — safe, documented pattern, not fixed to keep the diff minimal).
- **No frontend component/integration tests exist** (no Jest/Playwright/Vitest set up). All frontend verification in this session was done via live integration testing against a running backend (see Section 6, bug #5) — this caught real bugs unit tests wouldn't have, but it's manual and not repeatable as CI. **Recommended next step for a new team: add Playwright for at least the core trade-flow path.**

---

## 9. Concrete next steps, roughly in priority order

1. **Ratings & Reputation (PRD Module 20)** — was originally scoped as MVP but never built. Cheapest high-value gap to close.
2. **Playwright end-to-end tests** covering the full trade flow through the real proxy — codify the manual verification from Section 6 so it can't silently regress.
3. **CI pipeline** (GitHub Actions or similar) running `pytest` + `next build`/`lint` on every PR — none exists yet.
4. **Real GPS for logistics** (Module 15/16) — replace manual status-text updates with device-reported coordinates; this is the natural next increment before attempting live map tracking.
5. **Dispute resolution as a real object** (Module 21) — currently just a status flag; needs an actual `Dispute` model, evidence upload (can reuse the `documents` app), and at minimum a manual-admin-arbitrates workflow.
6. **Email notifications** — currently in-app only; wire Celery + Redis (both already anticipated in `requirements.txt` comments) for async email on key events.
7. **S3-compatible storage** — currently local disk via a Docker volume; fine for a pilot, not for real scale or multi-instance deployment.
8. **The financial modules (7–12, 14, 17–18)** — do not start these without first deciding on a licensed banking/payments partner. This is a business/legal decision, not an engineering one.

---

## 10. How to pick this up

```bash
git clone <backend repo> && cd backend && git log --oneline && git tag   # see full history
git clone <frontend repo> && cd frontend && git log --oneline && git tag

# Local dev (no Docker):
cd backend && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python manage.py migrate && python manage.py runserver
cd ../frontend && npm install && npm run dev   # BACKEND_INTERNAL_URL defaults to localhost:8000

# Full stack via Docker:
cp .env.example .env   # fill in real secrets
docker compose up --build
```

See `backend/README.md` and `frontend/README.md` for per-service detail, and the two earlier planning documents (`tradeafric_mvp_plan.md`, `tradeafric_django_setup_guide.md`) for the original architecture reasoning if useful — this document supersedes them on *current status*, but they still have useful detail on the reasoning behind the app/model split.
