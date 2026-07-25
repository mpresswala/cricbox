from cricbox.utils import TABLE_ATTRS

import django_tables2 as tables


class PlayersTable(tables.Table):
    batting = tables.TemplateColumn("Batting", verbose_name="", linkify=("batsman-stats", [tables.A("id")]))
    bowling = tables.TemplateColumn(
        "Bowling",
        linkify=("bowling-stats-name", [tables.A("id")]),
        verbose_name="",
    )
    member_since = tables.DateColumn(verbose_name="Joined")
    playing_role = tables.Column(verbose_name="Role")
    batting_style = tables.Column(verbose_name="Bat")
    bowling_style = tables.Column(verbose_name="Bowl")
    first_name = tables.Column(verbose_name="Name", linkify=("player-profile", [tables.A("id")]))

    def render_first_name(self, value, record):
        return f"{value} {record.last_name}"

    class Meta:
        attrs = TABLE_ATTRS
        sequence = (
            "first_name",
            "member_since",
            "playing_role",
            "batting_style",
            "bowling_style",
            "batting",
            "bowling",
        )
