# STATE-ONLY migration — see the detailed comment in
# match/migrations/0006_alter_match_season.py for why. Same field pattern
# (Appointment.season regenerates its choices from datetime.now().year every
# year), same SQLite table-rebuild-vs-SQL-view hazard, same fix.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0002_auto_20250521_1209'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='appointment',
                    name='season',
                    field=models.IntegerField(choices=[(1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026)], default=2026, verbose_name='Season'),
                ),
            ],
            database_operations=[],
        ),
    ]
