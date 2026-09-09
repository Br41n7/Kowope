from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import core.schema  # noqa: F401 — registers the cookie-auth scheme with drf-spectacular

urlpatterns = [
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
