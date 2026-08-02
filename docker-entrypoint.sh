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
# since this entrypoint is shared by both. Each worker also gets 4 threads
# so a slow request (slow query, stalled external call, etc.) doesn't block
# every other visitor behind it.
#
# Worker class is our TimeoutThreadWorker (cricbox/gunicorn_worker.py) —
# briefly reverted to plain gthread on 2026-08-01 after Cloudflare Shield
# cut down a flood of edge connections that was the active problem that
# day, but re-added 2026-08-02: CPU burst-credit throttling on the Fly
# Machine can independently strand a thread on a connection that goes
# stale mid-write, and plain gthread has no way to ever recover that
# thread. See gunicorn_worker.py for the full history and reasoning.
#
# --keep-alive 75: gunicorn's default is 2s, but requests arrive through
# fly-proxy, which pools/reuses connections to the Machine and — per Fly
# staff on the community forum — only closes an idle one after 60s of no
# activity. With the 2s default, gunicorn was closing its end of a pooled
# connection long before fly-proxy considered it stale, so fly-proxy would
# periodically hand a "keep-alive" request to a connection gunicorn had
# already torn down, stalling the write until TimeoutThreadWorker's 30s
# guard (or, before that existed, nothing) killed it. 75s comfortably
# outlasts fly-proxy's 60s so gunicorn is never the one to close first.
exec .venv/bin/gunicorn cricbox.wsgi:application --chdir cricbox --bind "0.0.0.0:${PORT:-8000}" \
  --worker-class cricbox.gunicorn_worker.TimeoutThreadWorker --workers "${GUNICORN_WORKERS:-1}" \
  --threads 4 --keep-alive 75
