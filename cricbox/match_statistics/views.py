from io import BytesIO

from cricbox.filter_widgets import DatalistTextInput
from opposition.models import Opposition
from venue.models import Venue

from .models import MatchStatistics
from .tables import (
    BattingTable,
    BowlingTable,
    OppositionTable,
    SeasonTable,
    VenuesTable,
)

from django.db.models import Count, DecimalField, ExpressionWrapper, F, FloatField, Q
from django.http import HttpResponse
from django.views.generic.base import TemplateView

import django_filters
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin
from django_tables2.views import SingleTableMixin


# Create your views here.
class OppositionFilter(django_filters.FilterSet):
    season = django_filters.RangeFilter(field_name="match__season")
    match__venue__name__icontains = django_filters.CharFilter(
        field_name="match__venue__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "season-opposition-venue-options",
            lambda: Venue.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )

    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match__mtype"].label = "Type"
        self.filters["match__home_or_away"].label = "Home/Away"
        self.filters["match__venue__name__icontains"].label = "Venue"


class VenueFilter(django_filters.FilterSet):
    season = django_filters.RangeFilter(field_name="match__season")
    match__opposition__name__icontains = django_filters.CharFilter(
        field_name="match__opposition__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "season-venue-opposition-options",
            lambda: Opposition.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )

    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match__mtype"].label = "Type"
        self.filters["match__home_or_away"].label = "Home/Away"
        self.filters["match__opposition__name__icontains"].label = "Opposition"


class SeasonFilter(django_filters.FilterSet):
    match__opposition__name__icontains = django_filters.CharFilter(
        field_name="match__opposition__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "season-overview-opposition-options",
            lambda: Opposition.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )
    match__venue__name__icontains = django_filters.CharFilter(
        field_name="match__venue__name",
        lookup_expr="icontains",
        widget=DatalistTextInput(
            "season-overview-venue-options",
            lambda: Venue.objects.order_by("name").values_list("name", flat=True).distinct(),
        ),
    )

    class Meta:
        model = MatchStatistics
        fields = {
            "match__mtype": ["exact"],
            "match__home_or_away": ["exact"],
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
            MatchStatistics.objects
            .values("match__season")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") * 100.0 / F("played"), output_field=FloatField()),
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
            MatchStatistics.objects
            .values("match__opposition__name", "match__opposition_id")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") * 100.0 / F("played"), output_field=DecimalField()),
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
            MatchStatistics.objects
            .values("match__venue__name", "match__venue_id")
            .annotate(
                played=Count("match"),
                won=won,
                loss=loss,
                abandoned=abandoned,
                draw=draw,
                win_percent=ExpressionWrapper(F("won") * 100.0 / F("played"), output_field=DecimalField()),
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


def og_match_image(request, id):
    """Generate a simple OG image for a match scorecard."""
    try:
        ms = MatchStatistics.objects.select_related(
            "match__opposition", "match__venue", "result"
        ).get(id=id)
    except MatchStatistics.DoesNotExist:
        return HttpResponse(status=404)

    match = ms.match
    opponent = match.opposition.name if match.opposition else "Unknown"
    venue_name = match.venue.name if match.venue else "Unknown"
    result_name = ms.result.name if ms.result else "—"
    date_str = match.date.strftime("%d %b %Y")

    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 630
    img = Image.new("RGB", (width, height), (15, 23, 42))  # ink-900
    draw = ImageDraw.Draw(img)

    # Try to load a font, fall back to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except (OSError, IOError):
        title_font = subtitle_font = body_font = small_font = ImageFont.load_default()

    # Accent bar at top
    draw.rectangle([(0, 0), (width, 8)], fill=(234, 179, 8))  # brand-500 amber

    # Club name
    draw.text((48, 36), "LONDON FIELDS CC", fill=(234, 179, 8), font=subtitle_font)

    # Opponent + date
    draw.text((48, 90), f"vs {opponent}", fill=(255, 255, 255), font=title_font)
    draw.text((48, 158), f"{date_str}  ·  {venue_name}", fill=(156, 163, 175), font=body_font)

    # Score boxes
    box_y = 240
    # LF score
    draw.rounded_rectangle([(48, box_y), (340, box_y + 120)], radius=12, fill=(30, 41, 59))  # ink-800
    draw.text((68, box_y + 16), "LONDON FIELDS", fill=(156, 163, 175), font=small_font)
    lf_score = f"{ms.london_fields_score}/{ms.london_fields_wickets}" if ms.london_fields_score is not None else "—"
    lf_overs = f"({ms.london_fields_overs} ov)" if ms.london_fields_overs else ""
    draw.text((68, box_y + 48), lf_score, fill=(255, 255, 255), font=title_font)
    if lf_overs:
        draw.text((68, box_y + 88), lf_overs, fill=(156, 163, 175), font=small_font)

    # VS
    draw.text((388, box_y + 36), "VS", fill=(234, 179, 8), font=subtitle_font)

    # Opposition score
    draw.rounded_rectangle([(468, box_y), (760, box_y + 120)], radius=12, fill=(30, 41, 59))
    opp_label = opponent[:18].upper()
    draw.text((488, box_y + 16), opp_label, fill=(156, 163, 175), font=small_font)
    opp_score = f"{ms.opposition_score}/{ms.opposition_wickets}" if ms.opposition_score is not None else "—"
    opp_overs = f"({ms.opposition_overs} ov)" if ms.opposition_overs else ""
    draw.text((488, box_y + 48), opp_score, fill=(255, 255, 255), font=title_font)
    if opp_overs:
        draw.text((488, box_y + 88), opp_overs, fill=(156, 163, 175), font=small_font)

    # Result badge
    draw.rounded_rectangle([(48, box_y + 148), (280, box_y + 188)], radius=8, fill=(234, 179, 8))
    draw.text((68, box_y + 156), result_name.upper(), fill=(15, 23, 42), font=body_font)

    # Bottom text
    draw.text((48, height - 48), "londonfields.net", fill=(75, 85, 99), font=small_font)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")
