# TradeAfric Backend (MVP)

Django + DRF backend for the TradeAfric MVP — the core RFQ → Offer → Purchase Order → Logistics/Inspection trade flow.
See `../tradeafric_mvp_plan.md` and `../tradeafric_django_setup_guide.md` for the full architecture and scope this was built from.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # fill in real values if deploying
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API docs
Once running: http://localhost:8000/api/docs/ (Swagger UI, auto-generated from the code)

## Running tests
```bash
pytest -q
```
11 tests currently cover: registration/JWT issuance, KYC submit + admin-only review,
RFQ/Offer creation, the accept-offer → PurchaseOrder business logic (including the
permission check and the immutable terms snapshot), and order visibility scoping.

## What's implemented (MVP scope)
- `accounts` — registration, JWT login, role-based users, KYC submission + admin review
- `marketplace` — RFQ CRUD, Offer CRUD, negotiation messages, accept/reject
- `orders` — Purchase Order auto-created on offer acceptance, with an immutable terms snapshot
- `documents` — generic versioned document vault (attaches to any model via GenericForeignKey)
- `logistics` — logistics requests + manual shipment status updates
- `quality` — inspection requests + reports (with photos)
- `notifications` — in-app notifications, fired synchronously on key events (swap for Celery later)

## Deliberately NOT implemented (v2/v3 — see plan doc)
Escrow, bank guarantees, FX, wallets, financier/factoring marketplace, insurance marketplace,
AI credit/risk scoring, live GPS tracking, ERP integrations, public API/developer portal.
These require a licensed financial partner or significant additional scope — do not build
them ad hoc; revisit the plan doc's phasing first.

## Switching to Postgres
Set `DATABASE_URL` in `.env`, e.g.:
```
DATABASE_URL=postgres://user:password@localhost:5432/tradeafric
```
Then uncomment `psycopg2-binary` in `requirements.txt` and reinstall.

## Versioning
Git tags map to completed MVP milestones — see `git tag` in this repo:
`v0.1.0-accounts` → `v0.2.0-marketplace` → `v0.3.0-orders` → `v0.4.0-documents-logistics-quality`
→ `v0.5.0-notifications` → `v1.0.0-mvp`
