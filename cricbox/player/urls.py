from .views import PlayerCompareView, PlayersView, ProfileView, player_search

from django.urls import path

# path: players/
urlpatterns = [
    path("", PlayersView.as_view(), name="players"),
    path("search/", player_search, name="player-search"),
    path("compare/", PlayerCompareView.as_view(), name="player-compare"),
    path("profiles/<int:player_id>/", ProfileView.as_view(), name="player-profile"),
]
