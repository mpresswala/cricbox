"""Staging settings - mirrors production but on a separate host/DB."""
import os
from pathlib import Path

from .settings_fly import *  # noqa: F403

DATA_DIR = Path("/var/data")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-staging-key-do-not-use-in-prod-abc123"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db-staging.sqlite3"),
        "OPTIONS": {"init_command": "PRAGMA journal_mode=WAL;"},
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(DATA_DIR / "cache-staging"),
    }
}

ADMINS = []
MANAGERS = []
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SERVE_MEDIA = True
MEDIA_ROOT = str(DATA_DIR / "media-staging")

STATIC_ROOT = os.path.join(Path(__file__).resolve(strict=True).parent.parent, "staticfiles-staging")

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
