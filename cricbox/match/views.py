from cricbox.filter_widgets import DatalistTextInput
from cricbox.utils import INVALID_PLAYERS, PSEUDO_PLAYER_NAMES
from opposition.models import Opposition
from player.models import Player
from venue.models import Venue

from .models import Match
from .tables import AppearancesTable, FixturesTable

from django.db.models import Count
from django.db.models import Value as V
from django.db.models.functions import Concat, Lower, Trim

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


# Create your views here.
def _filter_player_full_name(queryset, _name, _value):
    # Applied after grouping in AppearancesView.get_queryset().
    return queryset


class AppearancesFilter(django_filters.FilterSet):
    opposition__name__icontains = django_filters.CharFilter(
        field_name="opposition__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "appearances-opposition-options",
            lambda: Opposition.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )
    venue__name__icontains = django_filters.CharFilter(
        field_name="venue__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "appearances-venue-options",
            lambda: Venue.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )
    players__first_name__icontains = django_filters.CharFilter(
        method=_filter_player_full_name,
        widget=DatalistTextInput(
            "appearances-player-options",
            lambda: (
                Player.objects
                .exclude(INVALID_PLAYERS)
                .annotate(full_name=Concat("first_name", V(" "), "last_name"))
                .order_by("first_name", "last_name")
                .values_list("full_name", flat=True)
                .distinct()
            ),
        ),
    )

    class Meta:
        model = Match
        fields = {
            "season": ["icontains"],
            "mtype": ["exact"],
            "home_or_away": ["exact"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["season__icontains"].label = "Year"
        self.filters["mtype"].label = "Type"
        self.filters["home_or_away"].label = "Home/Away"
        self.filters["opposition__name__icontains"].label = "Opposition"
        self.filters["venue__name__icontains"].label = "Venue"
        self.filters["players__first_name__icontains"].label = "Player"


class FixturesFilter(django_filters.FilterSet):
    opposition__name__icontains = django_filters.CharFilter(
        field_name="opposition__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "fixtures-opposition-options",
            lambda: Opposition.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )
    venue__name__icontains = django_filters.CharFilter(
        field_name="venue__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "fixtures-venue-options",
            lambda: Venue.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )

    class Meta:
        model = Match
        fields = {
            "mtype": ["exact"],
            "home_or_away": ["exact"],
            "season": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["season__icontains"].label = "Year"
        self.filters["mtype"].label = "Type"
        self.filters["home_or_away"].label = "Home/Away"
        self.filters["opposition__name__icontains"].label = "Opposition"
        self.filters["venue__name__icontains"].label = "Venue"


class AppearancesView(SingleTableMixin, FilterView):
    table_class = AppearancesTable
    model = Match
    filterset_class = AppearancesFilter
    template_name = "match/appearances.html"

    def get_queryset(self):
        # Drop the "Extras"/"Unknown" pseudo-players. Match on a normalised
        # (trimmed, lower-cased) name so e.g. "Extras " (no last name) is caught,
        # while real players such as "Wayne Unknown" are kept.
        #
        # Matches with no players recorded yet (e.g. future fixtures) must be
        # excluded *before* grouping: the M2M join otherwise produces a single
        # collapsed row with players__id=NULL, which survives the
        # normalised_name exclude() below (NULL never matches IN/NOT IN in
        # SQL) and then blows up the "player-profile" linkify with
        # NoReverseMatch since it has no id to link to.
        queryset = (
            Match.objects
            .filter(players__isnull=False)
            .values(
                "players__id",
                players__full_name=Concat("players__first_name", V(" "), "players__last_name"),
            )
            .annotate(appearances=Count("players__id"))
            .annotate(normalised_name=Lower(Trim("players__full_name")))
            .exclude(normalised_name__in=PSEUDO_PLAYER_NAMES)
            .order_by("-appearances")
        )
        player_query = self.request.GET.get("players__first_name__icontains", "").strip()
        if player_query:
            queryset = queryset.filter(players__full_name__icontains=player_query)
        return queryset


class FixtureView(SingleTableMixin, FilterView):
    table_class = FixturesTable
    model = Match
    filterset_class = FixturesFilter
    template_name = "match/fixtures.html"
