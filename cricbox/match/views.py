# Cricbox imports
from cricbox.utils import INVALID_PLAYERS_MATCH

from .models import Match
from .tables import AppearancesTable, FixturesTable

# Django imports
from django.db.models import Count
from django.db.models import Value as V
from django.db.models.functions import Concat

# Django third party apps
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


# Create your views here.
class AppearancesFilter(django_filters.FilterSet):
    class Meta:
        model = Match
        fields = {
            "season": ["icontains"],
            "mtype": ["exact"],
            "home_or_away": ["exact"],
            "opposition__name": ["icontains"],
            "venue__name": ["icontains"],
            "players__first_name": ["icontains"],
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
    class Meta:
        model = Match
        fields = {
            "mtype": ["exact"],
            "home_or_away": ["exact"],
            "opposition__name": ["icontains"],
            "venue__name": ["icontains"],
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
        return (
            Match.objects.values(
                "players__id",
                players__full_name=Concat("players__first_name", V(" "), "players__last_name"),
            )
            .annotate(appearances=Count("players__id"))
            .exclude(INVALID_PLAYERS_MATCH)
            .order_by("-appearances")
        )


class FixtureView(SingleTableMixin, FilterView):
    table_class = FixturesTable
    model = Match
    filterset_class = FixturesFilter
    template_name = "match/fixtures.html"
