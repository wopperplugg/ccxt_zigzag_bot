import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zigzag.settings")

app = Celery("zigzag")

# Загружаем настройки из settings.py (префикс CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи в приложениях
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
