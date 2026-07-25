import datetime
from decimal import Decimal

from django.db.models import Q

# There are 6 balls in an over. Overs are stored/entered as a decimal where the
# fractional part is the number of balls (e.g. 4.3 == 4 overs and 3 balls), so
# they cannot be summed arithmetically — the balls must be totalled and carried.
BALLS_PER_OVER = 6


def overs_to_balls(overs):
    """Convert an overs value (e.g. Decimal('4.3')) to a ball count (27)."""
    if not overs:
        return 0
    value = Decimal(str(overs))
    whole = int(value)
    balls = int(round((value - whole) * 10))
    return whole * BALLS_PER_OVER + balls


def balls_to_overs(balls):
    """Convert a ball count back to overs notation.

    Returns an int for a whole number of overs, otherwise a Decimal 'overs.balls'
    (e.g. 27 -> 4 (rendered "4"), 26 -> Decimal('4.2')).
    """
    if balls is None:
        return None
    overs, remaining = divmod(int(balls), BALLS_PER_OVER)
    return overs if remaining == 0 else Decimal(f"{overs}.{remaining}")


FIFTIES = Q(Q(runs__gt=49), Q(runs__lte=99))
HUNDREDS = Q(runs__gt=99)
FIVERS = Q(Q(wickets__gt=4))
INVALID_PLAYERS = Q(Q(first_name="Extras") | Q(first_name="Unknown") | Q(first_name=None))

# Placeholder "players" that stand in for byes/extras or unrecorded names; they
# must never appear in stats or appearances. Compared against a normalised
# (trimmed, lower-cased) name so "Extras " / "EXTRAS" all match, while real
# players like "Wayne Unknown" are unaffected.
PSEUDO_PLAYER_NAMES = ["extras", "unknown"]

# how_out values that are not actual dismissals (used to build dismissal
# breakdowns and to count genuine outs).
NON_DISMISSAL_WICKET_TYPES = ["Not Out", "Did Not Bat", "Unknown", "Retired Hurt", "Retired Out"]

TABLE_ATTRS = {"class": "stats-table"}

SITE_URLS = {
    "LONDON_FIELDS_MAP_URL": "https://osm.org/go/euu6cZFC?layers=N&way=4406359",
    "VPCCL_LEAGUE_TABLES_URL": "http://www.vpccl.co.uk/fixtures+results/2012/teams/londonfields.html",
    "VPCCL_URL": "http://www.vpccl.co.uk",
    "NELCL_URL": "https://nelcl.leaguerepublic.com/",
    "NELCL_RULES": "https://images.leaguerepublic.com/data/documents/209486375-league_rules_2021_1.docx",
    "NELCL_SCORECARD_PROCEDURES": "https://nelcl.leaguerepublic.com/l/newsArticle/match_report_procedure.html",
    "LONDON_FIELDS_SHED_RULES": "https://drive.google.com/file/d/145DTbtkD8e2SBZYsUFXy8ytqMHUaOmVV/view",
    "PUB_ON_THE_PARK_URL": "http://www.pubonthepark.com/",
    "LONDON_FIELDS_INSTAGRAM_PAGE": "https://www.instagram.com/londonfieldscc/",
    "YEAR": datetime.datetime.now().year,
}
