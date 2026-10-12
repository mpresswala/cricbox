from .views import MatchView, OppositionView, SeasonView, VenuesView, og_match_image

from django.urls import path

urlpatterns = [
    # ex: /season/
    path("overview/", SeasonView.as_view(), name="season-overview"),
    path("opposition/", OppositionView.as_view(), name="opposition-overview"),
    path("venues/", VenuesView.as_view(), name="venues-overview"),
    path("match/<int:id>/", MatchView.as_view(), name="match-overview"),
    path("og-image/<int:id>/", og_match_image, name="og-match-image"),
]
