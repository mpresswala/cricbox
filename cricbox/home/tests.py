# Django imports
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

# Smoke tests: every argument-free page should render without a server error.
# These give a safety net for framework upgrades and the frontend reskin.

# Named URLs that take no arguments.
NO_ARG_URL_NAMES = [
    "site-home",
    "site-about",
    "site-history",
    "site-links",
    "site-handbook",
    "site-documents",
    "site-match_manager",
    "site-stats",
    "site-positions",
    "site-performers",
    "fixtures-overview",
    "batsmen-stats",
    "bowling-stats-all",
    "match-appearances-player",
    "season-overview",
    "opposition-overview",
    "venues-overview",
    "players",
]


class PageSmokeTests(TestCase):
    """Each public page returns a non-server-error response on an empty DB."""

    def test_pages_render(self):
        for name in NO_ARG_URL_NAMES:
            with self.subTest(url_name=name):
                try:
                    url = reverse(name)
                except NoReverseMatch:
                    self.fail(f"URL name {name!r} could not be reversed")
                response = self.client.get(url)
                self.assertLess(
                    response.status_code,
                    500,
                    msg=f"{name} ({url}) returned {response.status_code}",
                )

    def test_sitemap_renders(self):
        response = self.client.get("/sitemap.xml")
        self.assertLess(response.status_code, 500)

    def test_admin_login_renders(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)


# Each stats table exposes sortable columns via ?sort=<accessor>. A wrong
# order_by on a column raises a FieldError (500), so exercise them all.
SORTABLE_COLUMNS = {
    "batsmen-stats": [
        "player_full_name", "innings", "runs_scored", "not_out",
        "highest", "average", "fifties", "hundreds",
    ],
    "bowling-stats-all": [
        "overs", "maidens", "runs", "total_wickets",
        "average", "strike_rate", "economy",
    ],
}


class TableSortingTests(TestCase):
    """Every sortable column orders without raising a server error."""

    def test_columns_are_sortable(self):
        for name, columns in SORTABLE_COLUMNS.items():
            base = reverse(name)
            for column in columns:
                with self.subTest(url_name=name, column=column):
                    response = self.client.get(base, {"sort": column})
                    self.assertLess(
                        response.status_code, 500,
                        msg=f"{name}?sort={column} returned {response.status_code}",
                    )
