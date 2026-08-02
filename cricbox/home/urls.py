from .views import (
    ClubRecordView,
    DismissalsView,
    DocumentView,
    PerformersView,
    PositionsView,
    RecordsView,
    about,
    handbook,
    healthz,
    history,
    home,
    links,
    match_manager,
    stats,
)

from django.urls import path
from django.views.decorators.cache import cache_page

urlpatterns = [
    path("", home, name="site-home"),
    path("healthz", healthz, name="healthz"),
    path("about/", about, name="site-about"),
    path("history/", history, name="site-history"),
    path("links/", links, name="site-links"),
    # The views cached below (positions, performers, records, results,
    # dismissals) share the same shape: no querystring/filter input, no
    # per-visitor content (no CSRF token, no login-state nav — checked
    # across home/templates), and each runs several full-history
    # aggregation queries with no natural ceiling, so they get slower every
    # season as more matches are recorded. Performers was confirmed as the
    # single largest source of 499/503s in Cloudflare's error logs; these
    # others are the same pattern and worth caching pre-emptively rather
    # than waiting for each to show up the same way.
    #
    # Deliberately NOT applied to the batsman/bowler/match FilterView pages:
    # those vary by querystring (season/type/player search etc.), so
    # cache_page would key on every distinct filter combination a visitor
    # (or a bot) constructs — much lower hit-rate benefit, and lets anyone
    # cheaply fill the cache with one-off entries. Caching those would need
    # a more targeted approach (e.g. caching the queryset, not the response).
    path(
        "honours/positions",
        cache_page(60 * 15)(PositionsView.as_view()),
        name="site-positions",
    ),
    path(
        "honours/performers",
        cache_page(60 * 15)(PerformersView.as_view()),
        name="site-performers",
    ),
    path("records/", cache_page(60 * 15)(RecordsView.as_view()), name="site-records"),
    path("results/", cache_page(60 * 15)(ClubRecordView.as_view()), name="site-results"),
    path("dismissals/", cache_page(60 * 15)(DismissalsView.as_view()), name="site-dismissals"),
    path("handbook/", handbook, name="site-handbook"),
    path("match-manager/", match_manager, name="site-match_manager"),
    path("stats/", stats, name="site-stats"),
    path("documents/", DocumentView.as_view(), name="site-documents"),
]
