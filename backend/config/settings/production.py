import sys

from .base import *  # noqa

DEBUG = False

# Fail loudly at startup rather than serving with an insecure default. A production
# deploy MUST set these explicitly — there is no safe fallback for either.
if SECRET_KEY == "django-insecure-change-me-in-production":  # noqa: F405
    sys.exit("SECURITY: SECRET_KEY is unset or using the insecure default. Set it in your environment.")

if ALLOWED_HOSTS in (["*"], []):  # noqa: F405
    sys.exit("SECURITY: ALLOWED_HOSTS must be set to your real domain(s) in production — refusing to start with '*'.")

# HTTPS is assumed to be terminated by a reverse proxy (nginx/Caddy) in front of gunicorn —
# see docker-compose.yml. These settings make Django aware of that and enforce it.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days; raise once you're confident HTTPS is stable
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files served via whitenoise (see requirements.txt + MIDDLEWARE below).
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
