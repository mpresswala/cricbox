#!/usr/bin/env python3
"""Convert a MySQL *data-only* dump into SQLite-loadable INSERT statements.

Usage:
    python scripts/mysql_dump_to_sqlite.py [--with-users] <mysql_dump.sql> <out.sql>

Produce the input with:
    mysqldump --no-create-info --skip-extended-insert --complete-insert \\
        --single-transaction --no-tablespaces <db> > london_fields_data.sql

The output only contains INSERTs for the cricket application tables (django_*
and auth_* tables are skipped — the fresh schema created by `migrate` already
populates them), with MySQL backslash string escapes rewritten to SQLite's
'' form. Load it into a migrated SQLite database with:
    sqlite3 db.sqlite3 < out.sql
(or see scripts/build_sqlite_from_mysql.sh which does the whole thing).

--with-users also carries over the `auth_user` accounts (usernames + password
hashes, so people can log in with their existing credentials). Group and
per-user permission assignments are NOT carried over, because they reference
auto-generated permission/content-type ids that differ in the fresh schema;
re-assign any groups in the admin afterwards (superusers are unaffected).
"""

import argparse

# Cricket application tables to load; everything else (auth_*, django_*) is
# recreated/populated by `migrate` and must not be duplicated here.
KEEP = {
    "appointment_types",
    "appointments",
    "batsmen",
    "batting_styles",
    "bowlers",
    "bowling_styles",
    "home_away",
    "home_clubdocument",
    "match_types",
    "matches",
    "matches_statistics",
    "news_items",
    "oppositions",
    "pictures",
    "pictures_player",
    "player_match_attributes",
    "player_skills",
    "players",
    "playing_roles",
    "podcasts",
    "podcasts_player",
    "results",
    "venues",
    "wicket_types",
}

# MySQL backslash escapes -> their literal characters.
MYSQL_ESC = {
    "0": "\x00",
    "b": "\x08",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


def convert_line(line):
    """Rewrite MySQL single-quoted string literals to SQLite form."""
    out = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == "'":
            i += 1
            val = []
            while i < n:
                ch = line[i]
                if ch == "\\" and i + 1 < n:
                    val.append(MYSQL_ESC.get(line[i + 1], line[i + 1]))
                    i += 2
                    continue
                if ch == "'":
                    if i + 1 < n and line[i + 1] == "'":  # escaped '' -> '
                        val.append("'")
                        i += 2
                        continue
                    i += 1
                    break
                val.append(ch)
                i += 1
            out.append("'" + "".join(val).replace("'", "''") + "'")
        else:
            out.append(c)
            i += 1
    return "".join(out)


def table_of(line):
    start = line.find("`")
    end = line.find("`", start + 1)
    return line[start + 1 : end]


def main(src, out, with_users=False):
    keep = set(KEEP)
    if with_users:
        keep.add("auth_user")

    kept = 0
    skipped = set()
    with (
        open(src, encoding="utf-8", errors="replace") as fin,
        open(out, "w", encoding="utf-8") as fout,
    ):
        fout.write("PRAGMA foreign_keys=OFF;\n")
        fout.write("BEGIN;\n")
        for line in fin:
            if not line.startswith("INSERT INTO `"):
                continue
            table = table_of(line)
            if table not in keep:
                skipped.add(table)
                continue
            fout.write(convert_line(line))
            kept += 1
        fout.write("COMMIT;\n")

    print(f"kept {kept} INSERT statements")
    if skipped:
        print("skipped tables:", ", ".join(sorted(skipped)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a MySQL data-only dump to SQLite INSERTs.")
    parser.add_argument("src", help="MySQL dump file")
    parser.add_argument("out", help="output SQLite .sql file")
    parser.add_argument(
        "--with-users",
        action="store_true",
        help="also carry over the auth_user accounts (usernames + password hashes)",
    )
    args = parser.parse_args()
    main(args.src, args.out, with_users=args.with_users)
