# TradeAfric MVP — Documentation, Code Plan & Build Workflow

This document is written so you (or any AI coding assistant) can pick it up cold and build the MVP without needing the original conversation. It's organized so you can feed one section at a time into an AI prompt and get a working, coherent piece back.

---

## Part 1 — MVP Scope (Locked)

**In scope for v1:**
- User registration + role-based accounts (Buyer, Seller, Admin, Logistics Partner, Inspector)
- KYC submission + manual admin review
- RFQ posting (buyer) + Offer submission (seller)
- Negotiation thread (simple chat/counter-offer, no video/voice)
- Digital Purchase Order generation on offer acceptance
- Document vault (upload/view/version POs, invoices, certificates)
- Basic logistics request + manual status updates (no live GPS yet)
- Basic quality inspection request + report upload (no AI scoring yet)
- Notifications (in-app, email)
- Admin panel (Django admin, customized) for KYC approval and dispute flagging
- Ratings (1–5 stars, buyer↔seller only)

**Explicitly out of scope for v1** (v2/v3 — do not build yet):
- Escrow, bank guarantees, FX, wallets (require a licensed financial partner — integrate later via API, don't build)
- Financier/invoice-factoring marketplace
- Insurance marketplace
- AI credit scoring / Trade Confidence Score / fraud detection
- Live GPS tracking, ERP integrations, public API/developer portal

---

## Part 2 — System Architecture

```
┌─────────────┐      REST/JSON       ┌──────────────────┐
│  Next.js     │ ───────────────────▶ │  Django + DRF     │
│  (frontend)  │ ◀─────────────────── │  (backend API)    │
└─────────────┘      JWT auth        └──────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    ▼                         ▼                     ▼
              PostgreSQL                Redis + Celery         S3-compatible
              (primary DB)            (async jobs, email,      storage (docs,
                                        notifications)          certificates)
```

- **Backend:** Django 5.x + Django REST Framework, PostgreSQL, Celery + Redis for async tasks (email, notifications), django-storages for S3.
- **Frontend:** Next.js (App Router), fetches the DRF API, JWT stored in httpOnly cookies.
- **Auth:** `djangorestframework-simplejwt` for token auth; role stored on the User model, permission classes per role.
- **File uploads:** direct-to-S3 presigned URLs where possible, or through Django for MVP simplicity.

---

## Part 3 — Django App Breakdown

Create one Django app per domain — do **not** put everything in one `core` app. This keeps prompts scoped (you can ask an AI to build "the marketplace app" in isolation).

### `accounts`
**Purpose:** users, roles, KYC.
```
User (extends AbstractUser)
  - role: enum [buyer, seller, admin, logistics, inspector]
  - phone
  - is_kyc_verified: bool

KYCProfile
  - user: FK(User)
  - business_name
  - registration_number
  - tax_id
  - address
  - status: enum [pending, approved, rejected]
  - reviewed_by: FK(User, null=True)
  - reviewed_at
```
**Endpoints:** `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /kyc/submit`, `PATCH /kyc/{id}/review` (admin only)

### `marketplace`
**Purpose:** RFQs, offers, negotiation.
```
RFQ
  - buyer: FK(User)
  - commodity, grade, quantity, unit
  - delivery_location, delivery_date
  - target_price
  - quality_verification_pref: enum [delivery_test, independent, sample]
  - payment_pref: enum [escrow, guarantee, credit]  # display only in MVP
  - status: enum [open, closed, cancelled]
  - created_at

Offer
  - rfq: FK(RFQ)
  - seller: FK(User)
  - price, delivery_period
  - quality_certs (file, optional)
  - status: enum [submitted, countered, accepted, rejected]
  - created_at

NegotiationMessage
  - offer: FK(Offer)
  - sender: FK(User)
  - message
  - attachment (file, optional)
  - created_at
```
**Endpoints:** RFQ CRUD (`/rfqs/`), Offer CRUD nested under RFQ (`/rfqs/{id}/offers/`), `POST /offers/{id}/accept`, `POST /offers/{id}/reject`, `GET/POST /offers/{id}/messages/`

### `orders`
**Purpose:** digital purchase orders.
```
PurchaseOrder
  - offer: FK(Offer, one-to-one)
  - buyer, seller: FK(User)
  - po_number (auto-generated, unique)
  - terms_snapshot: JSONField  # freeze price/qty/terms at acceptance time
  - status: enum [issued, in_progress, delivered, disputed, completed, cancelled]
  - created_at
```
**Endpoints:** auto-create on offer acceptance (signal or service call), `GET /orders/`, `GET /orders/{id}/`, `PATCH /orders/{id}/status`

### `documents`
**Purpose:** central document vault, works for any related object.
```
Document
  - owner: FK(User)
  - content_type + object_id  # GenericForeignKey to RFQ/Order/Offer
  - doc_type: enum [po, invoice, certificate, delivery_note, other]
  - file
  - version: int
  - uploaded_at
```
**Endpoints:** `POST /documents/`, `GET /documents/?object_id=&content_type=`, `GET /documents/{id}/versions/`

### `logistics`
**Purpose:** shipment requests and status (manual for MVP).
```
LogisticsRequest
  - order: FK(PurchaseOrder)
  - pickup_location, delivery_location
  - status: enum [requested, assigned, in_transit, delivered]
  - assigned_partner: FK(User, null=True)

ShipmentUpdate
  - request: FK(LogisticsRequest)
  - status
  - note
  - timestamp
```
**Endpoints:** `POST /logistics-requests/`, `GET /logistics-requests/{id}/`, `POST /logistics-requests/{id}/updates/`

### `quality`
**Purpose:** inspection requests and reports.
```
InspectionRequest
  - order: FK(PurchaseOrder)
  - status: enum [requested, scheduled, completed]
  - inspector: FK(User, null=True)

InspectionReport
  - request: FK(InspectionRequest, one-to-one)
  - findings (text)
  - certificate_file
  - photos (multiple — separate model `InspectionPhoto` with FK)
  - submitted_at
```
**Endpoints:** `POST /inspection-requests/`, `POST /inspection-requests/{id}/report/`

### `notifications`
**Purpose:** in-app + email notifications, triggered by Celery tasks on key events (offer received, PO issued, inspection completed).
```
Notification
  - user: FK(User)
  - type: enum [rfq_offer, po_issued, inspection_done, dispute, general]
  - message
  - is_read: bool
  - created_at
```
**Endpoints:** `GET /notifications/`, `PATCH /notifications/{id}/read`

### `core_admin` (not really an app — Django admin customization)
- Register all models with sensible `list_display`, `list_filter`
- Custom admin action: approve/reject KYC
- Custom admin view or filter for flagged disputes

---

## Part 4 — Next.js Frontend Structure

```
/app
  /auth/login, /auth/register
  /kyc/submit
  /buyer
    /dashboard
    /rfqs/new
    /rfqs/[id]              -> offers + negotiation thread
    /orders/[id]
  /seller
    /dashboard
    /rfqs                   -> browse open RFQs
    /offers/new?rfq=[id]
    /orders/[id]
  /orders/[id]/documents
  /orders/[id]/logistics
  /orders/[id]/inspection
  /notifications
  /admin
    /kyc-review
    /disputes
```
Shared components: `RFQCard`, `OfferCard`, `NegotiationThread`, `DocumentUploader`, `StatusBadge`, `RoleGuard` (route protection by role).

---

## Part 5 — End-to-End MVP Trade Flow

1. Buyer completes KYC → approved by admin
2. Buyer posts RFQ
3. Seller (KYC-approved) browses RFQs, submits Offer
4. Buyer + Seller negotiate via message thread
5. Buyer accepts Offer → `PurchaseOrder` auto-created, PO number generated
6. Seller requests inspection (optional) → Inspector submits report
7. Seller requests logistics → status updated manually as goods move
8. Seller uploads invoice → Buyer marks order `delivered`/`completed`
9. Both parties rate each other
10. Notifications fire at each transition (Celery)

---

## Part 6 — Build Order (Sprints)

| Sprint | Focus |
|---|---|
| 0 | Repo setup, Django + DRF + Next.js scaffolding, CI, env config, base User model |
| 1 | `accounts` app: registration, login (JWT), KYC submission + admin review |
| 2 | `marketplace` app: RFQ CRUD, Offer CRUD, negotiation messages |
| 3 | `orders` app: PO auto-generation on offer acceptance, PO detail view |
| 4 | `documents` app: upload/list/versioning, wire into orders/RFQs |
| 5 | `logistics` + `quality` apps: request creation, manual status updates, report upload |
| 6 | `notifications` app + Celery wiring; Django admin polish for `core_admin` |
| 7 | Ratings, end-to-end QA, deploy (staging → production) |

Build and test each app fully (models → serializers → views → tests) before starting the next — this keeps each AI-assisted coding session self-contained.

---

## Part 7 — Prompt-Engineering Guide (for coding this without Claude access)

When your subscription runs out, you can hand this document (or one section at a time) to any capable coding AI. Structure your prompts like this:

**1. Give context once per session, not per file:**
> "I'm building a Django REST Framework backend for a trade marketplace. Django 5.x, DRF, PostgreSQL, JWT auth via simplejwt. Here are the models for the `marketplace` app: [paste the model block from Part 3]. Follow standard DRF conventions: separate serializers.py, views.py using ViewSets, urls.py with a router."

**2. Ask for one layer at a time, not everything at once:**
- Prompt 1: "Write the models.py for this app based on the spec above."
- Prompt 2: "Now write serializers.py for these models, including nested serialization for offers under an RFQ."
- Prompt 3: "Now write views.py using DRF ViewSets, with permission checks: only the RFQ owner (buyer) can edit their RFQ, only sellers can create offers."
- Prompt 4: "Now write urls.py wiring these into a router."
- Prompt 5: "Now write basic tests for the accept-offer flow."

Asking for one file/layer per prompt gives far more reliable, reviewable output than asking for a whole app in one shot.

**3. Always specify business rules explicitly** — the AI won't infer them from the PRD:
> "An Offer can only be accepted if the RFQ status is still `open`. Accepting an offer must: set the offer status to `accepted`, close the RFQ, and create a PurchaseOrder with a snapshot of price/terms."

**4. For the frontend, prompt component-by-component:**
> "Write a Next.js (App Router) page component `app/buyer/rfqs/[id]/page.tsx` that fetches an RFQ and its offers from `GET /api/rfqs/{id}/`, displays offers in a list using an `OfferCard` component, and lets the buyer accept one."

**5. Review checklist after each AI-generated file:**
- Does it match the field names in Part 3 exactly?
- Are permissions enforced (role checks), not just authentication?
- Does it handle the "not found" / "not authorized" error cases?
- Is there a migration needed? Ask for it explicitly: "Now give me the makemigrations output / migration file."

---

## Part 8 — Best Practices Reminders

- **Never build escrow/FX/wallet logic yourself** — integrate a licensed provider's API when you reach that phase.
- Use Django's `permissions.py` classes per role — don't scatter `if user.role == 'buyer'` checks across views.
- Every state-changing action (offer accept, PO status change) should go through a **service function**, not directly in the view — makes it testable and reusable from Celery tasks/admin actions too.
- Write model-level tests for status transitions before writing views — these are the bugs that cost real trust (and money) later.
- Keep `terms_snapshot` on PurchaseOrder immutable once created — never let it silently follow changes to the original Offer.
- Version your API (`/api/v1/...`) from day one.
