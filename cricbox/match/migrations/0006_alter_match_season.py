# This is a STATE-ONLY migration. `season`'s `choices`/`default` are
# regenerated from datetime.now().year every time the app starts (see
# Match.YEARS in match/models.py), so this migration reappears every year
# once the current year rolls over — there's no way to avoid that while the
# field intentionally grows its choices annually.
#
# On SQLite, a real AlterField here would trigger a full table rebuild
# (SQLite has no ALTER COLUMN), which breaks: the `bowler_all_seasons` /
# `batsmen_all_seasons` SQL views (see home/migrations/0002_add_sql_views.py)
# reference the `matches` table by name and don't survive it being
# dropped/recreated mid-rebuild — confirmed locally: it left a dangling `no
# such table: matches` view error and then a foreign-key integrity failure on
# matches_statistics.match_id (Django's transaction rolled it back cleanly,
# but it must never be allowed to run for real against production).
#
# `choices` and `default` are Python-level validation only — SQLite has no
# CHECK/ENUM derived from them, so nothing in the actual schema needs to
# change. SeparateDatabaseAndState records the new field state for Django's
# migration history without executing any SQL at all, sidestepping the
# rebuild (and the view breakage) entirely. Same pattern applies to any
# future migration on `match.season` / `player.Appointment.season`.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0005_auto_20250521_1209'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='match',
                    name='season',
                    field=models.IntegerField(choices=[(1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026)], default=2026, verbose_name='Season'),
                ),
            ],
            database_operations=[],
        ),
    ]
