#!/usr/bin/env bash
#
# Build a ready-to-use SQLite database from a MySQL data-only dump.
#
# Usage:
#   scripts/build_sqlite_from_mysql.sh [--with-users] <mysql_dump.sql> [output_db]
#
# Produces <output_db> (default: db_import.sqlite3) with the current schema
# (via `migrate`) plus your data. Pass --with-users to also carry over the
# existing login accounts. Load it onto Render by seeding the Litestream bucket
# (see the README), or use it locally.
set -euo pipefail

WITH_USERS=""
if [ "${1:-}" = "--with-users" ]; then
  WITH_USERS="--with-users"
  shift
fi

DUMP="${1:?usage: build_sqlite_from_mysql.sh [--with-users] <mysql_dump.sql> [output_db]}"
OUT="${2:-db_import.sqlite3}"

REPO="$(cd "$(dirname "$0")/.." && pwd)"

# Use the project's virtualenv python if present.
if [ -n "${PYTHON:-}" ]; then
  :
elif [ -x "$REPO/.venv/bin/python" ]; then
  PYTHON="$REPO/.venv/bin/python"
else
  PYTHON="python"
fi

# Absolute output path (settings_local reads DJANGO_SQLITE_PATH).
OUT_DIR="$(cd "$(dirname "$OUT")" && pwd)"
OUT_ABS="$OUT_DIR/$(basename "$OUT")"

TMP_SQL="$(mktemp)"
trap 'rm -f "$TMP_SQL"' EXIT

echo "==> Converting MySQL dump -> SQLite INSERTs"
"$PYTHON" "$REPO/scripts/mysql_dump_to_sqlite.py" $WITH_USERS "$DUMP" "$TMP_SQL"

echo "==> Creating fresh schema in $OUT_ABS"
rm -f "$OUT_ABS" "$OUT_ABS-wal" "$OUT_ABS-shm"
DJANGO_SETTINGS_MODULE=cricbox.settings_local DJANGO_SQLITE_PATH="$OUT_ABS" \
  "$PYTHON" "$REPO/cricbox/manage.py" migrate --no-input >/dev/null

echo "==> Loading data"
"$PYTHON" - "$OUT_ABS" "$TMP_SQL" <<'PY'
import sqlite3, sys
db, sql = sys.argv[1], sys.argv[2]
con = sqlite3.connect(db)
con.executescript(open(sql, encoding="utf-8").read())
con.commit()
con.close()
PY

echo "==> Done: $OUT_ABS"
