from batsman.models import Batsman
from batsman.tables import BatsmenTable
from bowler.models import Bowler
from bowler.tables import BowlersTable
from cricbox.utils import INVALID_PLAYERS, NON_DISMISSAL_WICKET_TYPES, balls_to_overs
from match.models import Match

from .models import Player
from .tables import PlayersTable

from django.db.models import Count, F
from django.views.generic import TemplateView

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

# Create your views here.


class PlayersFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = {
            "first_name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["first_name__icontains"].label = "Player"


class PlayersView(SingleTableMixin, FilterView):
    template_name = "player/player.html"
    table_class = PlayersTable
    filterset_class = PlayersFilter
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Player.objects.exclude(INVALID_PLAYERS).all().order_by("first_name")


class ProfileView(TemplateView):
    model = Player
    template_name = "player/profile.html"

    def get_context_data(self, **kwargs):
        player_id = self.kwargs.get("player_id")
        context = super().get_context_data(**kwargs)
        context["batting"] = BatsmenTable(Batsman.stat_objects.filter(player_id=player_id), exclude="player")
        context["bowling"] = BowlersTable(Bowler.stat_objects.filter(player_id=player_id), exclude="player")
        context["player"] = Player.objects.filter(id=player_id)[0]
        context["match_league"] = list(Match.objects.filter(players__id=player_id, mtype__name="League"))
        context["match_friendly"] = list(Match.objects.filter(players__id=player_id, mtype__name="Friendly"))
        context["match_vpccl"] = list(Match.objects.filter(players__id=player_id, mtype__name="VPCCL"))

        # Headline career figures (the stat managers return aggregated dict rows).
        batting = Batsman.stat_objects.filter(player_id=player_id).first()
        bowling = Bowler.stat_objects.filter(player_id=player_id).first()
        if bowling:
            bowling = {**bowling, "overs": balls_to_overs(bowling["total_balls"])}
        context["batting_summary"] = batting
        context["bowling_summary"] = bowling
        context["appearances"] = Match.objects.filter(players__id=player_id).count()

        # Personal records: best innings with the bat and ball.
        context["best_batting"] = (
            Batsman.objects.filter(player_id=player_id)
            .select_related("how_out", "match_statistics__match__opposition")
            .order_by("-runs")
            .first()
        )
        context["best_bowling"] = (
            Bowler.objects.filter(player_id=player_id)
            .select_related("match_statistics__match__opposition")
            .order_by("-wickets", "runs")
            .first()
        )

        # How this player gets out.
        dismissals = list(
            Batsman.objects.filter(player_id=player_id)
            .exclude(how_out__name__in=NON_DISMISSAL_WICKET_TYPES)
            .values(dismissal=F("how_out__name"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        total = sum(row["count"] for row in dismissals)
        for row in dismissals:
            row["percent"] = round(row["count"] / total * 100, 1) if total else 0
        context["dismissals"] = dismissals
        return context
