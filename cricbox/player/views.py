from batsman.models import Batsman
from batsman.tables import BatsmenTable
from bowler.models import Bowler
from bowler.tables import BowlersTable
from cricbox.utils import INVALID_PLAYERS, NON_DISMISSAL_WICKET_TYPES, balls_to_overs
from match.models import Match
from match_statistics.models import MatchStatistics

from .models import Player
from .tables import PlayersTable

from django.db.models import Count, F, Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

# Create your views here.


_ZERO_BATTING = {
    "innings": 0,
    "runs_scored": 0,
    "not_out": 0,
    "highest": 0,
    "average": None,
    "fifties": 0,
    "hundreds": 0,
}
_ZERO_BOWLING = {
    "overs": 0,
    "total_wickets": 0,
    "average": None,
    "economy": None,
    "strike_rate": None,
    "fives": 0,
}


def _parse_from_date(value):
    if not value:
        return None
    try:
        return parse_date(value)
    except ValueError:
        return None


def _parse_player_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _appearance_count(player_id, from_date=None):
    match_filter = {"players__id": player_id}
    batting_filter = {"player_id": player_id}
    bowling_filter = {"player_id": player_id}
    if from_date:
        match_filter["date__gte"] = from_date
        batting_filter["match_statistics__match__date__gte"] = from_date
        bowling_filter["match_statistics__match__date__gte"] = from_date

    match_ids = set(Match.objects.filter(**match_filter).values_list("id", flat=True))
    match_ids.update(Batsman.objects.filter(**batting_filter).values_list("match_statistics__match_id", flat=True))
    match_ids.update(Bowler.objects.filter(**bowling_filter).values_list("match_statistics__match_id", flat=True))
    return len(match_ids)


def _player_summary(player_id, from_date=None):
    """Career batting/bowling summary + appearances for one player, or None.

    Missing batting/bowling records are zero-filled so a genuine 0 (e.g. no
    hundreds) shows as 0 rather than being mistaken for missing data; rate
    stats that are undefined (no wickets/overs) stay None -> rendered as "—".
    """
    player = Player.objects.filter(id=player_id).first()
    if player is None:
        return None
    batting_filter = {"player_id": player_id}
    bowling_filter = {"player_id": player_id}
    if from_date:
        batting_filter["match_statistics__match__date__gte"] = from_date
        bowling_filter["match_statistics__match__date__gte"] = from_date

    batting = Batsman.stat_objects.filter(**batting_filter).first() or _ZERO_BATTING
    bowling = Bowler.stat_objects.filter(**bowling_filter).first()
    bowling = {**bowling, "overs": balls_to_overs(bowling["total_balls"])} if bowling else _ZERO_BOWLING
    return {
        "player": player,
        "batting": batting,
        "bowling": bowling,
        "appearances": _appearance_count(player_id, from_date),
    }


def player_search(request):
    """HTMX type-ahead: return players and match reports matching ?q=."""
    query = request.GET.get("q", "").strip()
    results = []
    report_results = []
    if query:
        results = (
            Player.objects
            .exclude(INVALID_PLAYERS)
            .annotate(full_name_annotated=Concat("first_name", Value(" "), "last_name"))
            .filter(full_name_annotated__icontains=query)
            .order_by("first_name", "last_name")[:8]
        )
        report_results = (
            MatchStatistics.objects
            .select_related("match__opposition")
            .filter(
                Q(report_headline__icontains=query)
                | Q(report__icontains=query)
                | Q(match__opposition__name__icontains=query)
            )
            .exclude(Q(report_headline__isnull=True) | Q(report_headline=""))
            .order_by("-match__date")[:8]
        )
    return render(
        request,
        "player/_search_results.html",
        {"results": results, "report_results": report_results, "query": query},
    )


class PlayerCompareView(TemplateView):
    template_name = "player/compare.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        a_id = self.request.GET.get("a")
        b_id = self.request.GET.get("b")
        from_date_raw = self.request.GET.get("from_date", "")
        from_date = _parse_from_date(from_date_raw)
        a_selected_id = _parse_player_id(a_id)
        b_selected_id = _parse_player_id(b_id)
        context["players"] = [
            {
                "id": player.pk,
                "full_name": player.full_name(),
                "is_a_selected": player.pk == a_selected_id,
                "is_b_selected": player.pk == b_selected_id,
            }
            for player in Player.objects.exclude(INVALID_PLAYERS).order_by("first_name", "last_name")
        ]
        context["a_id"], context["b_id"] = a_id, b_id
        context["from_date"] = from_date_raw
        context["from_date_active"] = from_date
        context["a"] = _player_summary(a_id, from_date) if a_id else None
        context["b"] = _player_summary(b_id, from_date) if b_id else None
        return context


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
            Batsman.objects
            .filter(player_id=player_id)
            .select_related("how_out", "match_statistics__match__opposition")
            .order_by("-runs")
            .first()
        )
        context["best_bowling"] = (
            Bowler.objects
            .filter(player_id=player_id)
            .select_related("match_statistics__match__opposition")
            .order_by("-wickets", "runs")
            .first()
        )

        # How this player gets out.
        dismissals = list(
            Batsman.objects
            .filter(player_id=player_id)
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
