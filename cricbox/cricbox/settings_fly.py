"""Production settings for Fly.io (SQLite on a Fly Volume).

Run with:  DJANGO_SETTINGS_MODULE=cricbox.settings_fly

The SQLite database and uploaded media live on a Fly Volume mounted at
DJANGO_DATA_DIR (default /var/data — the same path used on Render, so
docker-entrypoint.sh and litestream.yml need no changes between platforms).
Static files are served by WhiteNoise. Only DJANGO_SECRET_KEY is strictly
required; the app's own *.fly.dev hostname is picked up automatically.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Volume mount point (holds the DB and media across deploys).
DATA_DIR = Path(os.environ.get("DJANGO_DATA_DIR", "/var/data"))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False

# Add custom domains via DJANGO_ALLOWED_HOSTS (comma-separated). The app's
# own <name>.fly.dev host is added automatically from FLY_APP_NAME, which
# Fly sets on every Machine.
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
_fly_app_name = os.environ.get("FLY_APP_NAME")
if _fly_app_name:
    ALLOWED_HOSTS.append(f"{_fly_app_name}.fly.dev")

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Who gets emailed when a request raises an unhandled 500. Defaults to
# Mufaddal's address; override with DJANGO_ADMIN_EMAIL if needed.
ADMINS = [("Mufaddal", os.environ.get("DJANGO_ADMIN_EMAIL", "muffizone@gmail.com"))]
MANAGERS = ADMINS

# SMTP is optional: if DJANGO_EMAIL_HOST isn't set, mail is written to the
# console log instead of sent, so a missing/incomplete secret never breaks
# the site — it just means error emails silently don't go out.
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "cricbox@example.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL  # From: address on Django's error emails
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)

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
    "cricbox.middleware.HealthCheckMiddleware",
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

# SQLite on the Fly Volume. WAL mode improves concurrency and makes online
# backups (litestream / .backup) safe.
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

# Static files served by WhiteNoise from the deploy image (rebuilt each
# deploy); media lives on the Fly Volume.
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

# Security: the Fly Proxy terminates TLS and forwards the original scheme,
# same convention as Render.
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
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        # Emails ADMINS the full traceback + request data on any unhandled
        # 500, the same detail Django shows on the DEBUG error page.
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# django-unfold admin theme
from cricbox.unfold_config import UNFOLD  # noqa: E402,F401
