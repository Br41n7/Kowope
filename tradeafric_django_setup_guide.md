# TradeAfric MVP — Django Setup, Dependencies, Code Layout & Git Versioning Guide

Companion to `tradeafric_mvp_plan.md`. This document takes you from an empty folder to a running, version-controlled Django + DRF project structured for the MVP.

---

## Part 1 — Prerequisites

- Python 3.12+
- PostgreSQL 15+ (running locally or via Docker)
- Redis 7+ (for Celery — can be added in Sprint 6, not needed day one)
- Git
- (Optional but recommended) Docker + Docker Compose for Postgres/Redis so you're not installing them bare-metal

---

## Part 2 — Step-by-Step Project Initialization

```bash
# 1. Create project folder and git repo
mkdir tradeafric-backend && cd tradeafric-backend
git init
git branch -M main

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Upgrade pip and install Django + core tooling
pip install --upgrade pip
pip install django djangorestframework

# 4. Start the Django project (note the trailing dot — keeps manage.py at root)
django-admin startproject config .

# 5. Create the apps (one per domain from the plan)
python manage.py startapp accounts
python manage.py startapp marketplace
python manage.py startapp orders
python manage.py startapp documents
python manage.py startapp logistics
python manage.py startapp quality
python manage.py startapp notifications

# 6. Move each app into an `apps/` folder to keep root clean (optional but recommended)
mkdir apps
mv accounts marketplace orders documents logistics quality notifications apps/
# then add apps/ to PYTHONPATH via config/settings — see Part 5

# 7. First commit
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "media/" >> .gitignore
git add .
git commit -m "chore: initial Django project scaffold with app skeletons"
```

---

## Part 3 — Pip Dependencies

Create `requirements.txt`. Pin versions so your environment stays reproducible.

```txt
# Core
Django==5.1.4
djangorestframework==3.15.2
django-environ==0.11.2          # .env-based settings management
psycopg2-binary==2.9.10         # PostgreSQL driver

# Auth
djangorestframework-simplejwt==5.3.1

# Filtering / pagination / API polish
django-filter==24.3
drf-spectacular==0.28.0         # auto-generated OpenAPI/Swagger docs

# File storage (for documents app — S3-compatible)
django-storages==1.14.4
boto3==1.35.90

# Async tasks (add when you reach Sprint 6 — notifications/Celery)
celery==5.4.0
redis==5.2.1

# CORS (needed since Next.js runs on a different origin in dev)
django-cors-headers==4.6.0

# Testing
pytest==8.3.4
pytest-django==4.9.0
factory-boy==3.3.1              # test data factories

# Dev quality-of-life
django-extensions==3.2.3
python-dotenv==1.0.1
```

```bash
pip install -r requirements.txt
```

Install these in stages, not all at once — add `celery`/`redis` only when you actually start Sprint 6, so your early commits don't carry unused dependencies.

---

## Part 4 — Full Project Directory Layout

```
tradeafric-backend/
├── manage.py
├── requirements.txt
├── .env                          # not committed
├── .env.example                  # committed — template for required vars
├── .gitignore
├── README.md
├── config/                       # Django project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py                   # root urlconf, includes each app's urls
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # shared settings
│   │   ├── dev.py                # local dev overrides
│   │   └── production.py         # prod overrides
│   └── celery.py                 # added in Sprint 6
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py        # role-based permission classes
│   │   ├── admin.py
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   └── test_views.py
│   │   └── migrations/
│   ├── marketplace/               # same internal layout as accounts
│   ├── orders/
│   ├── documents/
│   ├── logistics/
│   ├── quality/
│   └── notifications/
├── core/                          # cross-app shared code
│   ├── permissions.py             # e.g. IsOwner, IsKYCVerified
│   ├── pagination.py
│   └── services/                  # business-logic service functions (not in views)
│       ├── offer_service.py       # e.g. accept_offer() -> creates PurchaseOrder
│       └── notification_service.py
└── media/                         # local dev file uploads (gitignored)
```

**Why `core/services/`:** state-changing business logic (e.g. "accepting an offer creates a PO") should live in a plain Python function, not inside a DRF view. This makes it callable from views, Celery tasks, admin actions, and tests without duplication — and it's exactly the kind of function you can hand to an AI prompt in isolation ("write `accept_offer(offer, actor)` given these two models").

---

## Part 5 — Settings Structure

`config/settings/base.py` — shared settings, reads secrets from environment:

```python
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "apps.accounts",
    "apps.marketplace",
    "apps.orders",
    "apps.documents",
    "apps.logistics",
    "apps.quality",
    "apps.notifications",
]

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://localhost:5432/tradeafric"),
}
```

`.env.example` (commit this, not `.env`):
```
SECRET_KEY=changeme
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/tradeafric
```

Set `DJANGO_SETTINGS_MODULE=config.settings.dev` in your shell or `manage.py` for local work.

---

## Part 6 — Git Versioning Scope, Tied to MVP Features

Use a simple, disciplined branch + tag strategy — this doubles as your project status tracker.

**Branch strategy:**
```
main                  -> always deployable
feature/accounts-kyc
feature/marketplace-rfq-offer
feature/orders-po
feature/documents-vault
feature/logistics-basic
feature/quality-basic
feature/notifications
```
One feature branch per sprint from the build plan. Merge to `main` via PR (even solo — self-review the diff before merging) once tests pass.

**Commit message convention** (Conventional Commits — makes history genuinely useful later):
```
feat(accounts): add KYC submission and admin review endpoint
fix(marketplace): prevent offer creation on closed RFQ
test(orders): add PO auto-generation test on offer acceptance
chore: add drf-spectacular for API docs
docs: update README with local setup steps
```

**Tagging scope to MVP features** — tag `main` at the end of each sprint so you always have a working checkpoint to roll back to:
```bash
git tag -a v0.1.0-accounts -m "Accounts + KYC complete"
git tag -a v0.2.0-marketplace -m "RFQ + Offer + negotiation complete"
git tag -a v0.3.0-orders -m "PO generation complete"
git tag -a v0.4.0-documents -m "Document vault complete"
git tag -a v0.5.0-logistics-quality -m "Logistics + quality requests complete"
git tag -a v0.6.0-notifications -m "Notifications + admin polish complete"
git tag -a v1.0.0-mvp -m "MVP feature-complete: end-to-end trade flow working"
git push origin --tags
```

This gives you (or a future collaborator) a version history that maps 1:1 to the sprint table in the plan doc — `v1.0.0-mvp` is the commit where every MVP feature in Part 1 of the plan is done.

---

## Part 7 — Coding Order (Commands + What to Build, Per Sprint)

**Sprint 1 — accounts**
```bash
git checkout -b feature/accounts-kyc
# build apps/accounts/models.py (User, KYCProfile), serializers, views, urls, permissions
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py test apps.accounts
git add . && git commit -m "feat(accounts): user roles, KYC submission and review"
git checkout main && git merge feature/accounts-kyc
git tag -a v0.1.0-accounts -m "Accounts + KYC complete"
```

**Sprint 2 — marketplace** (repeat the same pattern: branch → build → migrate → test → merge → tag)
```bash
git checkout -b feature/marketplace-rfq-offer
python manage.py makemigrations marketplace
python manage.py migrate
python manage.py test apps.marketplace
```

Continue this exact pattern for `orders`, `documents`, `logistics`, `quality`, `notifications` — same five commands, different app name, matching the sprint table from the plan document.

**After every app:** wire its `urls.py` into `config/urls.py`:
```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.marketplace.urls")),
    path("api/v1/", include("apps.orders.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.logistics.urls")),
    path("api/v1/", include("apps.quality.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
```
`drf-spectacular`'s `/api/docs/` gives you live, always-current API documentation for free as you build — check it after every app.

---

## Part 8 — Testing Setup

`pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = tests.py test_*.py *_tests.py
```
Run tests per app as you finish it: `pytest apps/accounts/` — don't wait until the end to test everything at once.

---

## Part 9 — README.md Skeleton (commit this on day one)

```markdown
# TradeAfric Backend (MVP)

## Setup
1. python3 -m venv venv && source venv/bin/activate
2. pip install -r requirements.txt
3. cp .env.example .env  (fill in real values)
4. python manage.py migrate
5. python manage.py runserver

## API docs
Once running: http://localhost:8000/api/docs/

## Versioning
See git tags — each tag maps to a completed MVP feature (accounts, marketplace, orders, documents, logistics/quality, notifications, v1.0.0-mvp).
```

---

This gives you a repo where, at any point, `git log --oneline` and `git tag` alone tell you (or an AI you paste this into later) exactly what's built and what's next.
