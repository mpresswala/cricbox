from .views import (
    DocumentView,
    PerformersView,
    PositionsView,
    about,
    handbook,
    history,
    home,
    links,
    match_manager,
    stats,
)

from django.urls import path

urlpatterns = [
    path("", home, name="site-home"),
    path("about/", about, name="site-about"),
    path("history/", history, name="site-history"),
    path("links/", links, name="site-links"),
    path("honours/positions", PositionsView.as_view(), name="site-positions"),
    path("honours/performers", PerformersView.as_view(), name="site-performers"),
    path("handbook/", handbook, name="site-handbook"),
    path("match-manager/", match_manager, name="site-match_manager"),
    path("stats/", stats, name="site-stats"),
    path("documents/", DocumentView.as_view(), name="site-documents"),
]
