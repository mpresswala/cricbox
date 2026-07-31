from cricbox.tables import OversColumn
from cricbox.utils import TABLE_ATTRS
from player.models import Player

import django_tables2 as tables


class Scorecard(tables.Table):
    name = tables.Column(orderable=False)
    first_innings = tables.Column(orderable=False)
    second_innings = tables.Column(orderable=False)

    class Meta:
        attrs = TABLE_ATTRS


class HonoursTable(tables.Table):
    name = tables.Column(linkify=("player-profile", [tables.A("name_id")]))
    season = tables.Column()

    class Meta:
        attrs = TABLE_ATTRS


class NotablePerformancesTable(tables.Table):
    player = tables.Column(linkify=("player-profile", [tables.A("player_id")]))
    runs = tables.Column()
    wickets = tables.Column()
    season = tables.Column(accessor="match_statistics__match__season")
    match = tables.Column(accessor="match_statistics__match")
    mtype = tables.Column(accessor="match_statistics__match__mtype")
    result = tables.Column(accessor="match_statistics__result")

    class Meta:
        attrs = TABLE_ATTRS


class VeteransTable(tables.Table):
    full_name = tables.Column(
        linkify=("player-profile", [tables.A("id")]),
        verbose_name="Player Name",
        order_by=("first_name", "last_name"),
    )
    member_since = tables.Column(accessor="member_since", verbose_name="Member Since")

    class Meta:
        model = Player  # Associate the table with the Player model
        fields = ("full_name", "member_since")  # Specify only the fields you want to display
        attrs = TABLE_ATTRS  # Use your existing table attributes if needed


class BestPlayer(tables.Table):
    name = tables.Column(linkify=("player-profile", [tables.A("id")]))
    season = tables.Column()
    total = tables.Column()

    class Meta:
        attrs = TABLE_ATTRS


class ClubDocs(tables.Table):
    name = tables.Column()
    description = tables.Column()
    document = tables.FileColumn()

    class Meta:
        attrs = TABLE_ATTRS


class HighestScoresTable(tables.Table):
    player = tables.Column(linkify=("player-profile", [tables.A("player_id")]))
    runs = tables.Column(verbose_name="Score")
    how_out = tables.Column(verbose_name="How Out")
    opposition = tables.Column(accessor="match_statistics__match__opposition", verbose_name="Opposition")
    season = tables.Column(accessor="match_statistics__match__season", verbose_name="Season")

    class Meta:
        attrs = TABLE_ATTRS
        orderable = False


class BestBowlingTable(tables.Table):
    player = tables.Column(linkify=("player-profile", [tables.A("player_id")]))
    figures = tables.Column(verbose_name="Figures", order_by=("-wickets", "runs"))
    overs = OversColumn(verbose_name="Overs")
    opposition = tables.Column(accessor="match_statistics__match__opposition", verbose_name="Opposition")
    season = tables.Column(accessor="match_statistics__match__season", verbose_name="Season")

    class Meta:
        attrs = TABLE_ATTRS
        orderable = False


class SeasonAggregateTable(tables.Table):
    """Shared shape for 'most runs/wickets in a season' (dict rows)."""

    name = tables.Column(linkify=("player-profile", [tables.A("player_id")]), verbose_name="Player")
    season = tables.Column(verbose_name="Season")
    total = tables.Column(verbose_name="Total")

    class Meta:
        attrs = TABLE_ATTRS
        orderable = False


class TeamTotalsTable(tables.Table):
    london_fields_score = tables.Column(verbose_name="Total")
    result = tables.Column(verbose_name="Result")
    opposition = tables.Column(accessor="match__opposition", verbose_name="Opposition")
    venue = tables.Column(accessor="match__venue", verbose_name="Venue")
    season = tables.Column(accessor="match__season", verbose_name="Season")

    class Meta:
        attrs = TABLE_ATTRS
        orderable = False


class DismissalsTable(tables.Table):
    dismissal = tables.Column(verbose_name="Dismissal")
    count = tables.Column(verbose_name="Count")
    percent = tables.Column(verbose_name="% of dismissals")

    class Meta:
        attrs = TABLE_ATTRS
        orderable = False
