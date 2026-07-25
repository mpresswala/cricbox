import datetime
import random
from random import randint

from batsman.models import Batsman, WicketType
from bowler.models import Bowler
from match.models import HomeAway, Match, MatchType, PlayerSkill
from match_statistics.models import MatchStatistics, Result
from opposition.models import Opposition
from player.models import (
    Appointment,
    AppointmentType,
    BattingStyle,
    BowlingStyle,
    Player,
    PlayingRole,
)
from venue.models import Venue

from .choices import (
    APPOINTMENT_TYPES,
    BATTING_STYLES,
    BOWLING_STYLES,
    EVENT_FIRST,
    HOME_AWAY,
    MATCH_TYPE,
    PLAYER_SKILLS,
    PLAYING_ROLES,
    RESULT,
    WICKET_TYPES,
)

start_date = datetime.date(1997, 1, 1)

end_date = datetime.date(2020, 2, 1)

time_between_dates = end_date - start_date

days_between_dates = time_between_dates.days

# add seed data to models
seed_structuring = {
    PlayingRole: PLAYING_ROLES,
    BattingStyle: BATTING_STYLES,
    BowlingStyle: BOWLING_STYLES,
    AppointmentType: APPOINTMENT_TYPES,
    WicketType: WICKET_TYPES,
    MatchType: MATCH_TYPE,
    HomeAway: HOME_AWAY,
    PlayerSkill: PLAYER_SKILLS,
    Result: RESULT,
}

for k, v in seed_structuring.items():
    for x in v:
        x = k(name=x[1])
        x.save()

for i in range(1, 100):
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    p = Player(
        i,
        first_name=f"FOO{str(i)}",
        last_name=f"FAA{str(i)}",
        email=f"foo{str(i)}@email.com",
        playing_role=PLAYING_ROLES[randint(0, len(PLAYING_ROLES) - 1)][0],
        batting_style=BATTING_STYLES[randint(0, len(BATTING_STYLES) - 1)][0],
        bowling_style=BOWLING_STYLES[randint(0, len(BOWLING_STYLES) - 1)][0],
        member_since=random_date,
    )
    p.save()

for i in range(1, 20):
    o = Opposition(i, name=f"Oppo{str(i)}")
    o.save()
    v = Venue(i, name=f"Venue{str(i)}")
    v.save()

p = Player.objects.all()
o = Opposition.objects.all()
v = Venue.objects.all()

for i in range(1, 250):
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    m = Match(
        season=random_date.year,
        date=random_date,
        mtype=MATCH_TYPE[randint(0, len(MATCH_TYPE) - 1)][0],
        home_or_away=HOME_AWAY[randint(0, 1)][0],
        venue=v[randint(0, len(v) - 1)],
        opposition=o[randint(0, len(o) - 1)],
    )
    m.save()
    first = randint(0, 80)
    players = p[first : first + 11]
    for player in players:
        m.players.add(player)
        m.save()

matches = Match.objects.all()

for match in matches:
    london_fields_score = randint(100, 250)
    opposition_score = randint(100, 250)
    result = "W" if london_fields_score > opposition_score else "L"
    match_stat = MatchStatistics(
        match=match,
        result=result,
        london_fields_overs=randint(0, 40),
        london_fields_score=london_fields_score,
        london_fields_wickets=randint(3, 10),
        opposition_score=opposition_score,
        opposition_overs=randint(0, 40),
        opposition_wickets=randint(3, 10),
        london_fields_first_event=EVENT_FIRST[randint(0, 1)][0],
    )
    match_stat.save()

match_stats = MatchStatistics.objects.all()

for match_stat in match_stats:
    players = match_stat.match.players.all()
    for plr in players[6:]:
        b = Bowler(
            player=plr,
            overs=randint(2, 6),
            maidens=randint(0, 3),
            runs=randint(15, 40),
            wickets=randint(0, 7),
            match_statistics=match_stat,
        )
        b.save()
    for idx, plr in enumerate(players[:7]):
        bat = Batsman(
            player=plr,
            runs=randint(0, 120),
            how_out=WICKET_TYPES[randint(0, len(WICKET_TYPES) - 1)][0],
            bowler=f"BAR{str(idx)}",
            match_statistics=match_stat,
        )
        bat.save()


# Add appointments
player_count = p.count()

YEARS = [year for year in range(1997, datetime.datetime.now().year + 1)]

for year in YEARS:
    for app in APPOINTMENT_TYPES:
        player = p[randint(0, player_count - 1)]
        a = Appointment(name=player, appointment_type=app[0], season=year)
        a.save()


# change existing appointments

for a in Appointment.objects.all():
    a.season = YEARS[randint(0, len(YEARS) - 1)]
    a.appointment_type = APPOINTMENT_TYPES[randint(0, len(APPOINTMENT_TYPES) - 1)][0]
    a.save()


# remove
# for i in Bowler.objects.filter(player__full_name__startswith="FOO"):
#     i.delete()

# for i in Player.objects.filter(full_name__startswith="FOO"):
#     i.delete()


# bulk delete
# Bowler.objects.all().delete()
# Batsman.objects.all().delete()
# MatchStatistics.objects.all().delete()
# Match.objects.all().delete()
# PlayingRole.objects.all().delete()
# BattingStyle.objects.all().delete()
# BowlingStyle.objects.all().delete()
# AppointmentType.objects.all().delete()
# WicketType.objects.all().delete()
# MatchType.objects.all().delete()
# HomeAway.objects.all().delete()
# PlayerSkill.objects.all().delete()
# Result.objects.all().delete()
