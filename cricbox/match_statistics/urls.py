from .views import MatchView, OppositionView, SeasonView, VenuesView

from django.urls import path

urlpatterns = [
    # ex: /season/
    path("overview/", SeasonView.as_view(), name="season-overview"),
    path("opposition/", OppositionView.as_view(), name="opposition-overview"),
    path("venues/", VenuesView.as_view(), name="venues-overview"),
    path("match/<int:id>/", MatchView.as_view(), name="match-overview"),
]
