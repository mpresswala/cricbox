#!/usr/bin/env bash
set -euo pipefail

DB="${DJANGO_DATA_DIR:-/var/data}/db.sqlite3"

# On a fresh/empty disk, restore the latest snapshot from the replica.
# No-ops if the DB already exists or no replica exists yet.
if [ -n "${LITESTREAM_BUCKET:-}" ]; then
  litestream restore -if-db-not-exists -if-replica-exists -o "$DB" "$DB"
fi

# Apply migrations (creates the schema on a truly fresh, un-restored disk).
.venv/bin/python cricbox/manage.py migrate --no-input

GUNICORN=".venv/bin/gunicorn cricbox.wsgi:application --chdir cricbox --bind 0.0.0.0:${PORT:-8000}"

# Run the app under Litestream so the WAL is replicated continuously; fall
# back to plain gunicorn if replication isn't configured.
if [ -n "${LITESTREAM_BUCKET:-}" ]; then
  exec litestream replicate -exec "$GUNICORN"
else
  exec $GUNICORN
fi
