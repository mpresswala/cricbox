from cricbox.tables import FloatColumn, SummingColumn
from cricbox.utils import TABLE_ATTRS

from .models import MatchStatistics

import django_tables2 as tables


class SeasonTable(tables.Table):
    played = tables.Column(verbose_name="P")
    won = tables.Column(verbose_name="W")
    draw = tables.Column(verbose_name="D")
    loss = tables.Column(verbose_name="L")
    abandoned = tables.Column(verbose_name="A")
    win_percent = FloatColumn(verbose_name="%")
    match__season = tables.TemplateColumn('<a href="{% url "fixtures-overview" %}?season={{ value }}">{{ value }}</a>')

    class Meta:
        attrs = TABLE_ATTRS
        model = MatchStatistics
        fields = (
            "match__season",
            "played",
            "won",
            "draw",
            "loss",
            "abandoned",
            "win_percent",
        )


class OppositionTable(tables.Table):
    played = tables.Column(verbose_name="P")
    won = tables.Column(verbose_name="W")
    draw = tables.Column(verbose_name="D")
    loss = tables.Column(verbose_name="L")
    abandoned = tables.Column(verbose_name="A")
    win_percent = FloatColumn(verbose_name="%")
    match__opposition__name = tables.TemplateColumn(
        '<a href="{% url "fixtures-overview" %}?opposition={{ record.match__opposition_id }}">{{ value }}</a>'
    )

    class Meta:
        attrs = TABLE_ATTRS
        model = MatchStatistics
        fields = (
            "match__opposition__name",
            "played",
            "won",
            "loss",
            "abandoned",
            "draw",
            "win_percent",
        )


class VenuesTable(tables.Table):
    played = tables.Column(verbose_name="P")
    won = tables.Column(verbose_name="W")
    draw = tables.Column(verbose_name="D")
    loss = tables.Column(verbose_name="L")
    abandoned = tables.Column(verbose_name="A")
    win_percent = FloatColumn(verbose_name="%")
    match__venue__name = tables.TemplateColumn(
        '<a href="{% url "fixtures-overview" %}?venue={{ record.match__venue_id }}">{{ value }}</a>'
    )

    class Meta:
        attrs = TABLE_ATTRS
        model = MatchStatistics
        fields = (
            "match__venue__name",
            "played",
            "won",
            "loss",
            "abandoned",
            "draw",
            "win_percent",
        )


class BowlingTable(tables.Table):
    player = tables.Column(verbose_name="Name")
    overs = tables.Column(verbose_name="O")
    maidens = tables.Column(verbose_name="M")
    runs = tables.Column(verbose_name="R")
    wickets = tables.Column(verbose_name="W")
    economy = tables.Column(verbose_name="Eco", orderable=False)
    average = tables.Column(verbose_name="Avg", orderable=False)
    strike_rate = tables.Column(verbose_name="S.R", orderable=False)

    class Meta:
        attrs = TABLE_ATTRS
        fields = (
            "player",
            "overs",
            "maidens",
            "runs",
            "wickets",
            "economy",
            "average",
            "strike_rate",
        )


class BattingTable(tables.Table):
    player = tables.Column(verbose_name="Name")
    scoring = tables.Column()
    how_out = tables.Column(verbose_name="How Out")
    bowler = tables.Column()
    runs = SummingColumn()

    class Meta:
        attrs = TABLE_ATTRS
        fields = ("player", "scoring", "how_out", "bowler", "runs")
