from cricbox.tables import CareerOversColumn, FloatColumn, SummingColumn, SummingOversColumn
from cricbox.utils import TABLE_ATTRS

import django_tables2 as tables


class BowlersTable(tables.Table):
    player_full_name = tables.Column(
        linkify=("player-profile", [tables.A("player_id")]),  # pyright: ignore[reportArgumentType]
        verbose_name="Player",
    )
    overs = CareerOversColumn(
        accessor="total_balls", order_by=("total_balls", "player_full_name"), verbose_name="Overs"
    )
    maidens = tables.Column(order_by=("maidens", "player_full_name"), verbose_name="Md")
    runs = tables.Column(order_by=("runs", "player_full_name"))
    total_wickets = tables.Column(order_by=("total_wickets", "player_full_name"), verbose_name="Wkts")
    average = FloatColumn(order_by=("average", "player_full_name"), verbose_name="Avg")
    strike_rate = FloatColumn(order_by=("strike_rate", "player_full_name"), verbose_name="SR")
    economy = FloatColumn(order_by=("economy", "player_full_name"), verbose_name="Eco")
    matches = tables.Column(
        order_by=("matches", "player_full_name"),
        verbose_name="Inn",
        linkify=("bowling-stats-name", [tables.A("player_id")]),  # pyright: ignore[reportArgumentType]
    )
    fours = tables.Column(verbose_name="4w")
    fives = tables.Column(verbose_name="5w")

    class Meta:
        attrs = TABLE_ATTRS
        fields = (
            "matches",
            "player_full_name",
            "overs",
            "maidens",
            "runs",
            "total_wickets",
            "average",
            "strike_rate",
            "economy",
        )
        sequence = (
            "player_full_name",
            "matches",
            "overs",
            "maidens",
            "runs",
            "total_wickets",
            "average",
            "strike_rate",
            "economy",
        )


class BowlerTable(tables.Table):
    runs = SummingColumn()
    maidens = SummingColumn()
    overs = SummingOversColumn()
    wickets = SummingColumn()
    match = tables.Column(
        verbose_name="Match",
        accessor="match_statistics",
        footer=lambda table: len(table.data),
    )
    economy = tables.Column(orderable=False)
    average = tables.Column(orderable=False)
    strike_rate = tables.Column(orderable=False)
    match_season = tables.Column(accessor="match_statistics__match__season", verbose_name="Season")
    match_type = tables.Column(accessor="match_statistics__match__mtype", verbose_name="Type")
    result = tables.Column(accessor="match_statistics__result__name", verbose_name="Result")

    class Meta:
        attrs = TABLE_ATTRS
        sequence = (
            "match_season",
            "match",
            "match_type",
            "overs",
            "maidens",
            "runs",
            "wickets",
            "economy",
            "average",
            "strike_rate",
            "result",
        )
        exclude = ("player", "id", "match_statistics")
