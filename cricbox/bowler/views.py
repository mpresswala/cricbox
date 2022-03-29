# Cricbox imports
from cricbox.filters import MatchFilter
from player.models import Player

from .models import Bowler
from .tables import BowlersTable, BowlerTable

# Django third party apps
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


class BowlerFilter(django_filters.FilterSet):
    class Meta:
        model = Bowler
        fields = {
            "match_statistics__match__season": ["icontains"],
            "match_statistics__match__mtype": ["exact"],
            "wickets": ["gte"],
            "runs": ["gte"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match_statistics__match__season__icontains"].label = "Year"
        self.filters["match_statistics__match__mtype"].label = "Type"
        self.filters["wickets__gte"].label = "Wickets"
        self.filters["runs__gte"].label = "Runs"


class BowlersFilter(MatchFilter):
    class Meta:
        model = Bowler
        fields = {
            "match_statistics__match__season": ["icontains"],
            "match_statistics__match__mtype": ["exact"],
            "player__first_name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["player__first_name__icontains"].label = "Player"


class BowlersView(SingleTableMixin, FilterView):
    filterset_class = BowlersFilter
    template_name = "bowler/bowler.html"
    table_class = BowlersTable
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Bowler.stat_objects.all()


class BowlerView(SingleTableMixin, FilterView):
    table_class = BowlerTable
    filterset_class = BowlerFilter
    template_name = "bowler/single_stats.html"

    def get_queryset(self):
        return Bowler.objects.filter(player__id=self.kwargs.get("id"))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        full_name = Player.objects.filter(id=self.kwargs.get("id"))[0].full_name
        context["full_name"] = full_name
        return context
