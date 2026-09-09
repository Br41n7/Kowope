class RelativeMediaURLMixin:
    """
    Strips `request` from the serializer context so FileField/ImageField values
    serialize as relative URLs (e.g. /media/x.pdf) instead of absolute ones built
    from Django's internal host. This matters because the frontend proxies /media/*
    through its own origin (see frontend/next.config.ts) — an absolute URL pointing
    at an internal-only backend host (e.g. http://backend:8000 in docker-compose)
    would be unreachable from the browser in production.
    """

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.pop("request", None)
        return context
