# Cricbox imports
from batsman.models import Batsman
from batsman.tables import BatsmenTable
from bowler.models import Bowler
from bowler.tables import BowlersTable
from cricbox.utils import INVALID_PLAYERS
from match.models import Match

from .models import Player
from .tables import PlayersTable

# Django imports
from django.views.generic import TemplateView

# Django third party apps
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

# Create your views here.


class PlayersFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = {
            "first_name": ["icontains"],
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["first_name__icontains"].label = "Player"


class PlayersView(SingleTableMixin, FilterView):
    template_name = "player/player.html"
    table_class = PlayersTable
    filterset_class = PlayersFilter
    table_pagination = {"per_page": 50}

    def get_queryset(self):
        return Player.objects.exclude(INVALID_PLAYERS).all().order_by("first_name")


class ProfileView(TemplateView):
    model = Player
    template_name = "player/profile.html"

    def get_context_data(self, **kwargs):
        player_id = self.kwargs.get("player_id")
        context = super().get_context_data(**kwargs)
        context["batting"] = BatsmenTable(Batsman.stat_objects.filter(player_id=player_id), exclude="player")
        context["bowling"] = BowlersTable(Bowler.stat_objects.filter(player_id=player_id), exclude="player")
        context["player"] = Player.objects.filter(id=player_id)[0]
        context["match_league"] = list(Match.objects.filter(players__id=player_id, mtype__name="League"))
        context["match_friendly"] = list(Match.objects.filter(players__id=player_id, mtype__name="Friendly"))
        context["match_vpccl"] = list(Match.objects.filter(players__id=player_id, mtype__name="VPCCL"))
        return context
