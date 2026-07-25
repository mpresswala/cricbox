[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# London Fields website
This Django project has been created for storing statistics, information and reports for a cricket club.

## Quick start

The django application is broken down into the following individual apps.

Theoretically this structure can be reused across any clubs with a similar format without much changes.

    batsman
    bowler
    home
    match
    match_statistics
    opposition
    player
    venue

### Dependencies (uv)

Python dependencies are managed with [uv](https://docs.astral.sh/uv/). It runs on
Django 6.0 and requires Python 3.12+.

```
uv sync                     # create .venv and install runtime + dev dependencies
uv sync --extra mysql       # also install the MySQL drivers (production)
uv run python cricbox/manage.py <command>
```

The MySQL drivers live in an optional `mysql` extra so local development (which
uses SQLite) does not need to build `mysqlclient`.

### Environment Variables Settings
Set the following environment variables before starting the application:
```
export DJANGO_SETTINGS_MODULE=cricbox.settings
export DJANGO_CRICBOX_PATH=<path-to-django-root-directory>
export DJANGO_SECRET_KEY=<secret-key>
export DJANGO_DB_DATABASE=<db-username>
export DJANGO_DB_HOSTNAME=<db-host>
export DJANGO_DB_USERNAME=<db-username>
export DJANGO_DB_PASSWORD=<db-password>
export DJANGO_SENTRY_URL=<sentry-url>
```

### Frontend (Tailwind CSS)

The public site is styled with [Tailwind CSS](https://tailwindcss.com/) (built
via the standalone CLI) plus [Alpine.js](https://alpinejs.dev/) and
[HTMX](https://htmx.org/), served as static files. Node.js is only needed to
rebuild the CSS — it is not required at runtime.

```
npm install                # once, to fetch the build tooling
npm run build:css          # compile cricbox/home/static/css/tailwind.css
npm run watch:css          # rebuild on template changes during development
npm run vendor             # refresh the vendored alpine.min.js / htmx.min.js
```

Source styles live in `cricbox/home/static/src/tailwind.css`. After changing
templates or styles, run `npm run build:css` and then `collectstatic` as usual.

### Local development

A SQLite-backed settings module is provided so the app can run without MySQL:

```
DJANGO_SETTINGS_MODULE=cricbox.settings_local uv run python cricbox/manage.py migrate
DJANGO_SETTINGS_MODULE=cricbox.settings_local uv run python cricbox/manage.py runserver
```
