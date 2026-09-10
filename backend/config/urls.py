from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve as serve_static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import core.schema  # noqa: F401 — registers the cookie-auth scheme with drf-spectacular
from core.views import healthz

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.marketplace.urls")),
    path("api/v1/", include("apps.orders.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.logistics.urls")),
    path("api/v1/", include("apps.quality.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# Always serve media directly, in DEBUG and in production alike. Django's own
# static() helper (django.conf.urls.static.static) silently no-ops whenever
# DEBUG=False — it's designed to be dev-only, and calling it here would look
# like it works but actually add nothing. We bypass that guard deliberately by
# wiring django.views.static.serve() directly.
#
# In the docker-compose topology, Caddy serves /media/* straight from the
# shared volume and this route is never actually hit — but Render (and any
# deployment without a fronting reverse proxy that owns the media volume) has
# no such layer, so Django must serve it itself. django.views.static.serve
# isn't the most performant option at real scale, but it's correct and
# sufficient for MVP-pilot traffic on a single instance with a persistent
# disk. Revisit (S3 + CDN) before scaling — see PROJECT_STATUS.md §9.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve_static, {"document_root": settings.MEDIA_ROOT}),
]
