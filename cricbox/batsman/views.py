# Cricbox imports
from cricbox.filters import MatchFilter
from player.models import Player

from .models import Batsman
from .tables import BatsmanTable, BatsmenTable

# Django third party apps
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


# filters
class BatsmanFilter(django_filters.FilterSet):
    class Meta:
        model = Batsman
        fields = {
            "match_statistics__match__season": ["icontains"],
            "match_statistics__match__mtype": ["exact"],
            "how_out": ["exact"],
            "runs": ["gte"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match_statistics__match__season__icontains"].label = "Year"
        self.filters["match_statistics__match__mtype"].label = "Type"
        self.filters["how_out"].label = "Wickets"
        self.filters["runs__gte"].label = "Runs"


class BatsmenFilter(MatchFilter):
    class Meta:
        model = Batsman
        fields = {
            "match_statistics__match__season": ["icontains"],
            "match_statistics__match__mtype": ["exact"],
            "player__first_name": ["icontains"],
            # "stat_objects__innings": ["gt"]
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["player__first_name__icontains"].label = "Player"


# Create your views here.
class BatsmenView(SingleTableMixin, FilterView):
    filterset_class = BatsmenFilter
    template_name = "batsman/batsman.html"
    table_class = BatsmenTable
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Batsman.stat_objects.all()


class BatsmanView(SingleTableMixin, FilterView):
    table_class = BatsmanTable
    filterset_class = BatsmanFilter
    template_name = "batsman/single_stats.html"

    def get_queryset(self):
        return Batsman.objects.filter(player__id=self.kwargs.get("id"))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        full_name = Player.objects.filter(id=self.kwargs.get("id"))[0].full_name
        context["full_name"] = full_name
        return context
