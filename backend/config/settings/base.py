from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    # local apps
    "apps.accounts",
    "apps.marketplace",
    "apps.orders",
    "apps.documents",
    "apps.logistics",
    "apps.quality",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# The frontend proxies /api/* to this backend via Next.js rewrites (see
# frontend/next.config.ts). Next's `:path*` catch-all rewrite does not preserve a
# trailing slash when reconstructing the destination URL, so with APPEND_SLASH's
# default redirect-based behavior, a POST would hit Django's "can't redirect a
# POST and keep the body" error, and a GET would loop forever (redirect adds the
# slash back → proxy strips it again on the next hop). The whole API is
# deliberately slash-less (see each app's urls.py: DefaultRouter(trailing_slash=False))
# to match exactly what the proxy actually delivers.
APPEND_SLASH = False

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Default: SQLite for zero-friction local dev. Set DATABASE_URL in .env to use Postgres:
# DATABASE_URL=postgres://user:password@localhost:5432/tradeafric
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# httpOnly auth cookies. In production (DEBUG=False) these are always sent over HTTPS
# and scoped SameSite=Lax, which works cleanly because the frontend proxies /api/*
# to this backend at the same origin (see frontend/next.config.ts) — no cross-site
# cookie or CORS configuration is needed.
AUTH_COOKIE_ACCESS = "ta_access"
AUTH_COOKIE_REFRESH = "ta_refresh"
AUTH_COOKIE_SECURE = not DEBUG
AUTH_COOKIE_SAMESITE = "Lax"

SPECTACULAR_SETTINGS = {
    "TITLE": "TradeAfric API",
    "DESCRIPTION": "Digital Trade Infrastructure Platform — MVP API",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "ENUM_NAME_OVERRIDES": {
        "StatusEnum": "apps.marketplace.models.RFQ.Status",
    },
}

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)
# Only relevant if something talks to the API cross-origin directly (e.g. a mobile app
# or direct API testing) — the Next.js frontend itself proxies same-origin and never
# needs CORS at all. Credentials must be allowed for cookie-based auth to work cross-origin.
CORS_ALLOW_CREDENTIALS = True
