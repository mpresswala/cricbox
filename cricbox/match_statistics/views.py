from .models import MatchStatistics
from .tables import (
    BattingTable,
    BowlingTable,
    OppositionTable,
    SeasonTable,
    VenuesTable,
)

# Django imports
from django.db.models import Count, DecimalField, ExpressionWrapper, F, FloatField, Q
from django.views.generic.base import TemplateView

# Django third party apps
import django_filters
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin
from django_tables2.views import SingleTableMixin


# Create your views here.
class OppositionFilter(django_filters.FilterSet):

    season = django_filters.RangeFilter(field_name="match__season")

    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
            "match__venue__name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match__mtype"].label = "Type"
        self.filters["match__home_or_away"].label = "Home/Away"
        self.filters["match__venue__name__icontains"].label = "Venue"


class VenueFilter(django_filters.FilterSet):

    season = django_filters.RangeFilter(field_name="match__season")

    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
            "match__opposition__name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match__mtype"].label = "Type"
        self.filters["match__home_or_away"].label = "Home/Away"
        self.filters["match__opposition__name__icontains"].label = "Opposition"


class SeasonFilter(django_filters.FilterSet):
    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
            "match__opposition__name": ["icontains"],
            "match__venue__name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match__mtype"].label = "Type"
        self.filters["match__home_or_away"].label = "Home/Away"
        self.filters["match__opposition__name__icontains"].label = "Opposition"
        self.filters["match__venue__name__icontains"].label = "Venue"


class SeasonView(SingleTableMixin, FilterView):
    table_class = SeasonTable
    model = MatchStatistics
    filterset_class = SeasonFilter
    template_name = "match_statistics/overview.html"

    def get_queryset(self):
        won = Count("result", filter=Q(result__name="Won"))
        loss = Count("result", filter=Q(result__name="Lost"))
        abandoned = Count("result", filter=Q(result__name="Abandoned"))
        draw = Count("result", filter=Q(result__name="Drawn"))

        return (
            self.model.objects.values("match__season")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") / F("played"), output_field=FloatField()),
            )
            .order_by("-match__season")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = "Season"
        return context


class OppositionView(SingleTableMixin, FilterView):
    table_class = OppositionTable
    model = MatchStatistics
    filterset_class = OppositionFilter
    template_name = "match_statistics/overview.html"

    def get_queryset(self):
        won = Count("result", filter=Q(result__name="Won"))
        loss = Count("result", filter=Q(result__name="Lost"))
        abandoned = Count("result", filter=Q(result__name="Abandoned"))
        draw = Count("result", filter=Q(result__name="Drawn"))

        return (
            self.model.objects.values("match__opposition__name", "match__opposition_id")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") / F("played"), output_field=DecimalField()),
            )
            .order_by("-won")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = "Opposition"
        return context


class VenuesView(SingleTableMixin, FilterView):
    table_class = VenuesTable
    model = MatchStatistics
    filterset_class = VenueFilter
    template_name = "match/fixtures.html"

    def get_queryset(self):
        won = Count("result", filter=Q(result__name="Won"))
        loss = Count("result", filter=Q(result__name="Lost"))
        abandoned = Count("result", filter=Q(result__name="Abandoned"))
        draw = Count("result", filter=Q(result__name="Drawn"))

        return (
            self.model.objects.values("match__venue__name", "match__venue_id")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") / F("played"), output_field=DecimalField()),
            )
            .order_by("-won")
        )


class MatchView(MultiTableMixin, TemplateView):
    template_name = "match_statistics/match_overview.html"

    def get_queryset(self, **kwargs):
        return MatchStatistics.objects.filter(id=self.kwargs.get("id"))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["match_stats"] = self.get_queryset(**kwargs)[0]
        return context

    def get_tables(self, **kwargs):
        match_stats = self.get_queryset(**kwargs)
        return [
            BowlingTable(match_stats[0].get_bowlers()),
            BattingTable(match_stats[0].get_batsman()),
        ]
