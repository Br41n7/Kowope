"""
Deployment utility: docker-compose's `depends_on` only waits for the Postgres
container to START, not for Postgres to be ready to accept connections. Without
this, gunicorn can crash-loop for the first few seconds of a fresh `docker compose up`.
"""
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for the database to be available before proceeding."

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=30, help="Max seconds to wait.")

    def handle(self, *args, **options):
        timeout = options["timeout"]
        waited = 0
        while waited < timeout:
            try:
                connections["default"].cursor()
                self.stdout.write(self.style.SUCCESS("Database is available."))
                return
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
                waited += 1
        self.stderr.write(self.style.ERROR(f"Database not available after {timeout}s — giving up."))
        raise SystemExit(1)
