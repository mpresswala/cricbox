# London Fields Cricket Club — cricbox

**Website:** https://londonfields.net
**Repository:** https://github.com/mpresswala/cricbox
**Live on:** Fly.io (app `cricbox`, region `lhr`)
**Domain:** londonfields.net (CNAME → cricbox.fly.dev)

## Stack

- **Django 6.0** on Python 3.12+
- **SQLite** with Litestream continuous replication to S3/B2
- **Tailwind CSS** (standalone CLI, compiled CSS committed — no Node at runtime)
- **Alpine.js + HTMX** (vendored, served as static files)
- **Gunicorn** (3 workers, `shared-cpu-4x` VM on Fly, 1.5GB RAM)
- **WhiteNoise** for static file serving
- **Admin:** django-unfold (modern admin skin)

## Apps

| App | Purpose |
|---|---|
| `batsman` | Batting stats, wicket types |
| `bowler` | Bowling stats |
| `home` | Public pages, Tailwind source styles |
| `match` | Match records and details |
| `match_statistics` | Derived match stats |
| `opposition` | Opposing clubs |
| `player` | Player profiles |
| `venue` | Grounds/venues |

## Quick commands

```bash
uv sync                          # install deps
uv run python cricbox/manage.py migrate
DJANGO_SETTINGS_MODULE=cricbox.settings_local uv run python cricbox/manage.py runserver
npm run build:css                # rebuild Tailwind after template changes
npm run watch:css                # auto-rebuild during dev
make format                      # ruff format
make lint                        # ruff check
make test                        # run tests
```

## Deployment

**Fly.io:** `fly deploy` — builds Docker image, restores DB from Litestream if volume is empty, runs migrate, serves via gunicorn+litestream.

- Health check removed intentionally (single Machine — 503s on check failure were worse than degraded perf)
- Settings: `cricbox.settings_fly` (set via `DJANGO_SETTINGS_MODULE` in fly.toml)
- Volume: `cricbox_data` mounted at `/var/data`
- Secrets managed via `fly secrets set`

**Render:** `render.yaml` blueprint also available (branch `modernize-frontend`, Docker, Starter plan, Frankfurt).

## Database

- SQLite in WAL mode on persistent volume
- Litestream streams WAL to object storage continuously
- `python cricbox/manage.py backup` for on-demand consistent snapshots

## Git

- SSH deploy key added to repo for write access
- Remote: `origin` → `git@github.com-mpresswala:mpresswala/cricbox.git`
