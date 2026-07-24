# Standard imports
import datetime

# Django imports
from django.db.models import Q

FIFTIES = Q(Q(runs__gt=49), Q(runs__lte=99))
HUNDREDS = Q(runs__gt=99)
FIVERS = Q(Q(wickets__gt=4))
INVALID_PLAYERS = Q(Q(first_name="Extras") | Q(first_name="Unknown") | Q(first_name=None))
INVALID_PLAYERS_MATCH = Q(
    Q(players__full_name="Extras") | Q(players__full_name=None) | Q(players__full_name="Unknown") | Q(players__id=None)
)

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
