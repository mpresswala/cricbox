import mysql.connector

from opposition.models import Opposition
from player.models import Player
from venue.models import Venue

old = mysql.connector.connect(
    user="django",
    password="Wz4vK36!DSeh%N",
    host="192.168.200.103",
    database="old_website",
)
old_cursor = old.cursor()
venues_query = "SELECT v_name FROM venues"
opposition_query = "SELECT t_name FROM teams"
player_query = "SELECT p_first_name, p_last_name, p_current FROM players"

old_cursor.execute(venues_query)

for v in old_cursor:
    x = Venue(name=v[0])
    x.save()

old_cursor.execute(opposition_query)
for o in old_cursor:
    x = Opposition(name=o[0])
    x.save()

old_cursor.execute(player_query)
for first, last, active in old_cursor:
    p = Player(first_name=first, last_name=last, active=bool(active))
    p.save()


"""
INSERT INTO london_fields.batsmen
(
    id,
    scoring,
    runs,
    bowler,
    how_out_id,
    match_statistics_id,
    player_id
)
SELECT bat_id, bat_score, bat_runs, bat_bowler_name, bat_how_out, bat_match_id, bat_batsman
FROM old_website.batting;
"""
