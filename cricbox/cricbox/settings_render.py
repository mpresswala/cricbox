"""Production settings for Render (SQLite on a persistent disk).

Run with:  DJANGO_SETTINGS_MODULE=cricbox.settings_render

The SQLite database and uploaded media live on a Render persistent disk
mounted at DJANGO_DATA_DIR (default /var/data). Static files are served by
WhiteNoise. Only DJANGO_SECRET_KEY is strictly required; DJANGO_ALLOWED_HOSTS
is picked up automatically when set.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Persistent disk mount point (holds the DB and media across deploys).
DATA_DIR = Path(os.environ.get("DJANGO_DATA_DIR", "/var/data"))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False

# Render sets RENDER_EXTERNAL_HOSTNAME to the service's *.onrender.com host.
# Add custom domains via DJANGO_ALLOWED_HOSTS (comma-separated).
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

INSTALLED_APPS = [
    "match_statistics.apps.MatchStatisticsConfig",
    "batsman.apps.BatsmanConfig",
    "home.apps.HomeConfig",
    "bowler.apps.BowlerConfig",
    "player.apps.PlayerConfig",
    "venue.apps.VenueConfig",
    "match.apps.MatchConfig",
    "opposition.apps.OppositionConfig",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tables2",
    "django_filters",
    "bootstrap4",
    "django.contrib.sitemaps",
    "django.contrib.sites",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cricbox.urls"

SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["cricbox/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cricbox.wsgi.application"

# SQLite on the persistent disk. WAL mode improves concurrency and makes
# online backups (litestream / .backup) safe.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db.sqlite3"),
        "OPTIONS": {"init_command": "PRAGMA journal_mode=WAL;"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# Static files served by WhiteNoise from the deploy slug (regenerated each
# build); media lives on the persistent disk.
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_ROOT = str(DATA_DIR / "media")
MEDIA_URL = "/media/"
# Django serves /media/ itself (fine for this traffic); see cricbox/urls.py.
SERVE_MEDIA = True

DJANGO_TABLES2_TEMPLATE = "django_tables2/tailwind.html"
CRISPY_TEMPLATE_PACK = "bootstrap4"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Security: Render terminates TLS and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# django-unfold admin theme
from cricbox.unfold_config import UNFOLD  # noqa: E402,F401
