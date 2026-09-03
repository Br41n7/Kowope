from apps.notifications.models import Notification


def notify(user, type_, message):
    """Create an in-app notification. Swap the body for a Celery task.delay() call
    once Celery is wired in (Sprint 6) — call sites elsewhere don't need to change."""
    return Notification.objects.create(user=user, type=type_, message=message)
