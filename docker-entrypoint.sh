#!/usr/bin/env bash
set -euo pipefail

DB="${DJANGO_DATA_DIR:-/var/data}/db.sqlite3"

# On a fresh/empty disk, restore the latest snapshot from the replica.
# Never fatal: a backup misconfiguration (e.g. bad credentials) must not stop
# the site from coming up.
if [ -n "${LITESTREAM_BUCKET:-}" ]; then
  litestream restore -if-db-not-exists -if-replica-exists -o "$DB" "$DB" \
    || echo "litestream: restore skipped or failed — continuing without it"
fi

# Apply migrations (creates the schema on a fresh, un-restored disk).
.venv/bin/python cricbox/manage.py migrate --no-input

# Start continuous replication in the background so a replication failure
# (e.g. bad credentials) cannot take the web process down. gunicorn runs in
# the foreground as the main process; the site stays up regardless.
if [ -n "${LITESTREAM_BUCKET:-}" ]; then
  litestream replicate || echo "litestream: replication stopped — site still serving" &
fi

# GUNICORN_WORKERS defaults to 1 (right for Render's 0.5-CPU Starter plan).
# Set it per-platform in fly.toml / render.yaml rather than hardcoding here,
# since this entrypoint is shared by both. Each worker also gets 8 threads
# so a slow request (slow query, stalled external call, etc.) doesn't block
# every other visitor behind it.
#
# Worker class reverted to plain gthread on 2026-08-01. We ran a custom
# TimeoutThreadWorker (cricbox/gunicorn_worker.py) for a while, which puts
# an explicit timeout on the response-write socket call — vanilla gthread
# leaves that call unbounded, so a client whose connection goes half-dead
# mid-response can pin a worker thread for minutes (kernel TCP timeout)
# instead of seconds. The actual incident that day turned out to be a
# flood of connections from Cloudflare's edge, not individual dead
# clients; enabling Cloudflare Shield cut that connection volume at the
# source, which made the timeout unnecessary. Trade-off if it's ever
# turned back off: a single stalled write can once again hang a thread
# indefinitely, since gunicorn's own --timeout watchdog can't detect a
# thread stuck in a blocking socket call. See gunicorn_worker.py (left in
# place, just unused) for the full writeup if this needs revisiting.
exec .venv/bin/gunicorn cricbox.wsgi:application --chdir cricbox --bind "0.0.0.0:${PORT:-8000}" \
  --worker-class gthread --workers "${GUNICORN_WORKERS:-1}" --threads 8
