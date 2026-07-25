from cricbox.utils import TABLE_ATTRS

import django_tables2 as tables


class AppearancesTable(tables.Table):
    players__full_name = tables.Column(verbose_name="Player", linkify=("player-profile", [tables.A("players__id")]))
    appearances = tables.Column()

    class Meta:
        attrs = TABLE_ATTRS
        fields = ("players__full_name", "appearances")


class FixturesTable(tables.Table):
    date = tables.Column()
    opposition = tables.Column()
    home_or_away = tables.Column()
    venue = tables.Column()
    mtype = tables.Column(verbose_name="Type")
    result = tables.Column(
        verbose_name="Result",
        accessor="matchstatistics__result",
        linkify=("match-overview", [tables.A("matchstatistics__id")]),
    )

    class Meta:
        attrs = TABLE_ATTRS
        fields = ("date", "opposition", "home_or_away", "venue", "mtype", "result")
