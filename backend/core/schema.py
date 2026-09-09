"""drf-spectacular extension so Swagger docs correctly describe cookie-based JWT auth."""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTScheme(OpenApiAuthenticationExtension):
    target_class = "core.authentication.CookieJWTAuthentication"
    name = "cookieAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "ta_access",
            "description": "httpOnly JWT access token cookie, set by /auth/login/ or /auth/register/.",
        }
