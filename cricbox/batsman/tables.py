from cricbox.tables import FloatColumn, SummingColumn
from cricbox.utils import TABLE_ATTRS

from .models import Batsman

import django_tables2 as tables


class BatsmenTable(tables.Table):
    player_full_name = tables.Column(
        linkify=("player-profile", [tables.A("player_id")]),  # pyright: ignore[reportArgumentType]
        verbose_name="Player",
    )
    innings = tables.Column(
        order_by=("innings", "player_full_name"),
        verbose_name="Inns",
        linkify=("batsman-stats", [tables.A("player_id")]),  # pyright: ignore[reportArgumentType]
    )
    runs_scored = tables.Column(order_by=("runs_scored", "player_full_name"), verbose_name="Runs")
    not_out = tables.Column(order_by=("not_out", "player_full_name"), verbose_name="NO")
    highest = tables.Column(order_by=("highest", "player_full_name"), verbose_name="HS")
    average = FloatColumn(order_by=("average", "player_full_name"), verbose_name="Avg")
    fifties = tables.Column(verbose_name="50")
    hundreds = tables.Column(verbose_name="100")

    class Meta:
        attrs = TABLE_ATTRS
        model = Batsman
        fields = (
            "player_full_name",
            "innings",
            "runs_scored",
            "not_out",
            "highest",
            "average",
            "fifties",
            "hundreds",
        )


class BatsmanTable(tables.Table):
    runs = SummingColumn()
    match = tables.Column(
        footer=lambda table: len(table.data),
        accessor="match_statistics",
        verbose_name="Match",
    )
    match_season = tables.Column(accessor="match_statistics__match__season", verbose_name="Season")
    match_type = tables.Column(accessor="match_statistics__match__mtype", verbose_name="Type")
    result = tables.Column(accessor="match_statistics__result__name", verbose_name="Result")

    class Meta:
        attrs = TABLE_ATTRS
        sequence = (
            "match_season",
            "match",
            "match_type",
            "scoring",
            "how_out",
            "bowler",
            "runs",
            "result",
        )
        model = Batsman
        exclude = ("player", "id", "match_statistics")
