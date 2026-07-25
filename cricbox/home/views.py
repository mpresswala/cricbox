from batsman.models import Batsman
from bowler.models import Bowler
from cricbox.utils import FIFTIES, FIVERS, HUNDREDS, NON_DISMISSAL_WICKET_TYPES, SITE_URLS
from match_statistics.models import MatchStatistics
from player.models import Appointment, Player

from .models import ClubDocument
from .tables import (
    BestBowlingTable,
    BestPlayer,
    ClubDocs,
    DismissalsTable,
    HighestScoresTable,
    HonoursTable,
    NotablePerformancesTable,
    Scorecard,
    SeasonAggregateTable,
    TeamTotalsTable,
    VeteransTable,
)

from django.db.models import Count, F, Q, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.views.generic import TemplateView

import django_filters
from django_filters.views import FilterView
from django_tables2.views import MultiTableMixin, SingleTableMixin

# Non-real "players" (byes/extras, unrecorded names) to keep out of records.
_REAL_PLAYERS = ~Q(player__first_name__in=["Extras", "Unknown"])
_NON_DISMISSALS = NON_DISMISSAL_WICKET_TYPES


def _season_totals(model, field):
    """Per-player, per-season Sum(field) rows for the leaderboard tables."""
    return (
        model.objects.filter(_REAL_PLAYERS)
        .values(
            "player_id",
            name=Concat("player__first_name", Value(" "), "player__last_name"),
            season=F("match_statistics__match__season"),
        )
        .annotate(total=Sum(field))
        .order_by("-total")[:10]
    )


# Create your views here.
def home(request):
    return render(request, "home/home.html", context=SITE_URLS)


def stats(request):
    return render(request, "home/stats.html")


def history(request):
    london_fields_scorecard = [
        {
            "name": "Osman",
            "first_innings": "5 b. Ripley",
            "second_innings": "6 c. Erwood",
        },
        {
            "name": "Chapman",
            "first_innings": "2 b. Ripley",
            "second_innings": "0 b. Ripley",
        },
        {
            "name": "Barber",
            "first_innings": "0 b. Ripley",
            "second_innings": "5 b. Jonson",
        },
        {
            "name": "James",
            "first_innings": "2 stumpt Trigg",
            "second_innings": "10 b. Ripley",
        },
        {
            "name": "Burrow",
            "first_innings": "0 st. Messenger",
            "second_innings": "6 c. Erwood",
        },
        {
            "name": "Lorimer",
            "first_innings": "3 b. Messenger",
            "second_innings": "5 c. Jonson",
        },
        {
            "name": "Pearce",
            "first_innings": "25 not out",
            "second_innings": "10 b. Ripley",
        },
        {
            "name": "Large",
            "first_innings": "1 b. Ripley",
            "second_innings": "6 c. Jonson",
        },
        {
            "name": "Low",
            "first_innings": "3 b. Ripley",
            "second_innings": "2 stumpt Ripley",
        },
        {
            "name": "Hoare",
            "first_innings": "4 b. Crisford",
            "second_innings": "1 run out",
        },
        {
            "name": "Yeats",
            "first_innings": "0 b. Messenger",
            "second_innings": "7 not out",
        },
        {"name": "Extras", "first_innings": "Byes 2", "second_innings": "Byes 3"},
        {"name": "Total", "first_innings": "47", "second_innings": "53"},
    ]
    clapton_scorecard = [
        {"name": "Glaizer", "first_innings": "16 b. Pearce"},
        {"name": "Robbin", "first_innings": "18 c. Lorimer"},
        {"name": "Hoare", "first_innings": "1 stumpt Barber"},
        {"name": "Jonson", "first_innings": "45 stumpt Osman"},
        {"name": "Messenger", "first_innings": "13 c. ditto"},
        {"name": "Prise", "first_innings": "21 c. Yeats"},
        {"name": "Crisford", "first_innings": "13 b. Pearce"},
        {"name": "Ripley", "first_innings": "4 b. Osman"},
        {"name": "Stewart", "first_innings": "2 c. Hoare"},
        {"name": "Jaines", "first_innings": "not out"},
        {"name": "Smith", "first_innings": "2 c. Osman"},
        {"name": "Extras", "first_innings": "Byes 11"},
        {"name": "Total", "first_innings": "149"},
    ]
    tables = [
        Scorecard(london_fields_scorecard),
        Scorecard(clapton_scorecard, exclude="second_innings"),
    ]

    return render(request, "home/history.html", {"tables": tables})


def about(request):
    return render(request, "home/about.html", context=SITE_URLS)


def links(request):
    return render(request, "home/links.html")


class PositionsView(MultiTableMixin, TemplateView):
    template_name = "home/club_positions.html"
    table_pagination = {"per_page": 50}

    def get_tables(self):
        return [
            HonoursTable(Appointment.objects.filter(appointment_type__name="Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="Vice Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="MidWeek Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="Fixturer").order_by("-season")),
            HonoursTable(
                Appointment.objects.filter(appointment_type__name="Domestic Tour Secretary").order_by("-season")
            ),
            HonoursTable(
                Appointment.objects.filter(appointment_type__name="International Tour Secretary").order_by("-season")
            ),
            VeteransTable(
                Player.objects.filter(life_member=True).order_by("-member_since__year"),
            ),
        ]


class PerformersView(MultiTableMixin, TemplateView):
    template_name = "home/club_performers.html"
    table_pagination = {"per_page": 50}

    best_batsman_query = """
        SELECT id, name, batsmen_all_seasons.season, total
        FROM (
                SELECT season, max(total) as max_total
                FROM batsmen_all_seasons
                GROUP BY season
            ) AS max_per_season
            inner join batsmen_all_seasons
                ON batsmen_all_seasons.season = max_per_season.season
                AND max_per_season.max_total = batsmen_all_seasons.total
        ORDER BY batsmen_all_seasons.season DESC;
    """

    best_bowler_query = """
        SELECT id, name, bowler_all_seasons.season, total
        FROM (
                SELECT season, max(total) as max_total
                FROM bowler_all_seasons
                GROUP BY season
            ) AS max_per_season
            inner join bowler_all_seasons
                ON bowler_all_seasons.season = max_per_season.season
                AND max_per_season.max_total = bowler_all_seasons.total
        ORDER BY bowler_all_seasons.season DESC;
    """

    def get_tables(self):
        return [
            NotablePerformancesTable(
                Batsman.objects.filter(FIFTIES).order_by("-match_statistics__match__season"),
                exclude="wickets",
            ),
            NotablePerformancesTable(
                Batsman.objects.filter(HUNDREDS).order_by("-match_statistics__match__season"),
                exclude="wickets",
            ),
            NotablePerformancesTable(
                Bowler.objects.filter(FIVERS).order_by("-match_statistics__match__season"),
                exclude="runs",
            ),
            BestPlayer(Batsman.objects.raw(self.best_batsman_query)),
            BestPlayer(Bowler.objects.raw(self.best_bowler_query)),
        ]


def handbook(request):
    return render(request, "home/handbook.html", SITE_URLS)


def match_manager(request):
    return render(request, "home/match_manager.html")


class DocFilter(django_filters.FilterSet):
    class Meta:
        model = ClubDocument
        fields = {
            "name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["name__icontains"].label = "Name"


class DocumentView(SingleTableMixin, FilterView):
    table_class = ClubDocs
    filterset_class = DocFilter
    template_name = "home/club_documents.html"

    def get_queryset(self):
        return ClubDocument.objects.all()


class RecordsView(MultiTableMixin, TemplateView):
    template_name = "home/records.html"
    table_pagination = {"per_page": 10}

    def get_tables(self):
        highest_scores = (
            Batsman.objects.filter(_REAL_PLAYERS)
            .select_related("player", "match_statistics__match__opposition")
            .order_by("-runs")[:10]
        )
        best_bowling = (
            Bowler.objects.filter(_REAL_PLAYERS)
            .select_related("player", "match_statistics__match__opposition")
            .order_by("-wickets", "runs")[:10]
        )
        team_totals = (
            MatchStatistics.objects.filter(london_fields_score__isnull=False)
            .select_related("match__opposition", "match__venue", "result")
            .order_by("-london_fields_score")[:10]
        )
        return [
            HighestScoresTable(highest_scores),
            BestBowlingTable(best_bowling),
            SeasonAggregateTable(_season_totals(Batsman, "runs")),
            SeasonAggregateTable(_season_totals(Bowler, "wickets")),
            TeamTotalsTable(team_totals),
        ]


class ClubRecordView(TemplateView):
    template_name = "home/club_record.html"

    @staticmethod
    def _summary(queryset):
        won = queryset.filter(result__name="Won").count()
        lost = queryset.filter(result__name="Lost").count()
        drawn = queryset.filter(result__name="Drawn").count()
        decisive = won + lost + drawn
        return {
            "played": queryset.count(),
            "won": won,
            "lost": lost,
            "drawn": drawn,
            "win_pct": round(won / decisive * 100, 1) if decisive else 0.0,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = MatchStatistics.objects.all()
        context["rows"] = [
            ("Overall", self._summary(stats)),
            ("Batted first", self._summary(stats.filter(london_fields_first_event=0))),
            ("Bowled first", self._summary(stats.filter(london_fields_first_event=1))),
            ("Home", self._summary(stats.filter(match__home_or_away__name="Home"))),
            ("Away", self._summary(stats.filter(match__home_or_away__name="Away"))),
        ]
        return context


class DismissalsView(TemplateView):
    template_name = "home/dismissals.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = list(
            Batsman.objects.filter(_REAL_PLAYERS)
            .exclude(how_out__name__in=_NON_DISMISSALS)
            .values(dismissal=F("how_out__name"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        total = sum(row["count"] for row in rows)
        for row in rows:
            row["percent"] = f"{(row['count'] / total * 100):.1f}%" if total else "0.0%"
        context["table"] = DismissalsTable(rows)
        context["total"] = total
        return context
