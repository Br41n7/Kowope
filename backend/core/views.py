"""
Deployment utility views — not part of the trade-flow API.
"""
from django.db import connections
from django.http import JsonResponse


def healthz(request):
    """
    Health check for Render (and any other platform) to poll before routing
    traffic to this instance. Verifies the DB connection is actually usable,
    not just that the process is running — a process that's up but can't
    reach Postgres should NOT be marked healthy.
    """
    try:
        connections["default"].cursor()
        db_ok = True
    except Exception:
        db_ok = False

    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "unhealthy", "database": db_ok}, status=status)
