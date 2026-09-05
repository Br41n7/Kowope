# TradeAfric MVP — Full Stack

Django REST backend + Next.js frontend implementing the core MVP trade flow:
register → KYC → RFQ → Offer → negotiation → accept (auto-issues Purchase Order) →
logistics request/tracking → quality inspection → notifications.

```
tradeafric/
├── backend/    Django + DRF API (see backend/README.md)
└── frontend/   Next.js app (see frontend/README.md)
```

## Running both together

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
cp .env.example .env.local
npm run dev                          # http://localhost:3000
```

Then visit http://localhost:3000, register as a buyer and a seller (two browser
sessions or incognito), approve their KYC from the Django admin at
http://localhost:8000/admin/ (or build `/admin/kyc-review` in as an admin-role
user), and run a full RFQ → Offer → Purchase Order flow.

## Status
Both halves have been built and verified together in this session:
- Backend: 11 automated tests passing, full trade-flow smoke test passing, git
  history tagged `v0.0.1-scaffold` → `v1.0.0-mvp`.
- Frontend: production build (`next build`) and lint both pass clean; every
  route was hit and returned 200 with the backend running; registration was
  exercised through the real API path end-to-end.

## Next steps
See `tradeafric_mvp_plan.md` and `tradeafric_django_setup_guide.md` for the
full architecture, MVP scope boundaries, and what's intentionally deferred
(escrow, FX, financier marketplace, insurance, AI scoring — all require a
licensed financial partner or significant additional scope).
