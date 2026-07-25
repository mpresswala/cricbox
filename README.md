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

## Deployment & migration steps

These are the steps to deploy this version, including upgrading an existing
install (which previously ran Django 3.1 and Poetry). **Back up the database
before upgrading.**

1. **Install prerequisites** — Python 3.12+, [uv](https://docs.astral.sh/uv/),
   and Node.js (only needed to build the CSS, not at runtime).

2. **Back up the production database.**

   ```
   mysqldump -h <host> -u <user> -p <database> > backup_$(date +%Y%m%d).sql
   ```

3. **Fetch the code and install dependencies** (including the MySQL drivers):

   ```
   git pull
   uv sync --extra mysql
   ```

4. **Set the environment variables** listed under *Environment Variables
   Settings* above (`DJANGO_SETTINGS_MODULE=cricbox.settings`, secret key,
   database credentials, Sentry URL, etc.).

5. **Apply database migrations:**

   ```
   uv run python cricbox/manage.py migrate
   ```

   Notes:
   - The Django 3.1 → 6.0 jump applies cleanly; there are no destructive
     operations. Run against the backup first if you want to rehearse it.
   - `batsman.0002_require_runs_and_how_out` is a form-level change only
     (`blank`), so it makes no schema change — it is applied/recorded but
     issues no `ALTER TABLE`.
   - The `home.0002_add_sql_views` migration (re)creates the
     `batsmen_all_seasons` / `bowler_all_seasons` SQL views. On a fresh
     database it is ordered to run after all table changes; on an existing
     database it is already applied and will not re-run.

6. **Build the frontend assets and collect static files:**

   ```
   npm install
   npm run build:css
   uv run python cricbox/manage.py collectstatic --noinput
   ```

7. **Create/verify the admin user** (if needed) and **restart the app server**
   (Apache/WSGI, gunicorn, etc.).

8. **Smoke-check** the deploy:

   ```
   uv run python cricbox/manage.py check --deploy
   ```

To roll back, redeploy the previous revision and restore the database from the
backup taken in step 2.
