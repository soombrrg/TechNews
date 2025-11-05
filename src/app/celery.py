import os
from typing import TYPE_CHECKING

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

celery = Celery("app")

celery.config_from_object("django.conf:settings", namespace="CELERY")

celery.autodiscover_tasks()


if TYPE_CHECKING:
    from celery.app.task import Task


@celery.task(bind=True)
def debug_task(self: "Task") -> None:
    print(f"Request: {self.request!r}")


__all__ = [
    "celery",
]
