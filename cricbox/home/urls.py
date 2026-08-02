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
    # Homepage: no querystring, no per-visitor content, and does real DB work
    # (next fixture, latest result/report, season summary) on every hit —
    # almost certainly the single highest-traffic URL on the site, so worth
    # caching even though it isn't as expensive as the views below.
    path("", cache_page(60 * 15)(home), name="site-home"),
    # healthz deliberately NOT cached — it must always reflect current
    # liveness, and it already does zero DB work (see home/views.py).
    path("healthz", healthz, name="healthz"),
    # Static content, no DB work at all (or close to it) — caching these
    # saves negligible time but is harmless, so applied for consistency.
    path("about/", cache_page(60 * 15)(about), name="site-about"),
    path("history/", cache_page(60 * 15)(history), name="site-history"),
    path("links/", cache_page(60 * 15)(links), name="site-links"),
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
    path("handbook/", cache_page(60 * 15)(handbook), name="site-handbook"),
    path("match-manager/", cache_page(60 * 15)(match_manager), name="site-match_manager"),
    path("stats/", cache_page(60 * 15)(stats), name="site-stats"),
    # Unlike the batsman/bowler/match FilterViews excluded above, this one's
    # underlying query (ClubDocument.objects.all()) is on a small table and
    # cheap even uncached, and the realistic search space for the name
    # filter is small (most visitors browse the unfiltered list rather than
    # searching) — so the querystring-cardinality concern that ruled out
    # caching the stats FilterViews doesn't really apply here.
    path("documents/", cache_page(60 * 15)(DocumentView.as_view()), name="site-documents"),
]
