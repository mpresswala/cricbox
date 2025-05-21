# Cricbox imports
from cricbox.settings import MEDIA_URL
from cricbox.utils import TABLE_ATTRS

# Django third party apps
import django_tables2 as tables
from player.models import Player

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
    full_name = tables.Column(linkify=("player-profile", [tables.A("id")]), verbose_name="Player Name")
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
