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
    "site-records",
    "site-results",
    "site-dismissals",
    "fixtures-overview",
    "batsmen-stats",
    "bowling-stats-all",
    "match-appearances-player",
    "season-overview",
    "opposition-overview",
    "venues-overview",
    "players",
    "player-compare",
    "player-search",
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
        "player_full_name",
        "innings",
        "runs_scored",
        "not_out",
        "highest",
        "average",
        "fifties",
        "hundreds",
    ],
    "bowling-stats-all": [
        "overs",
        "maidens",
        "runs",
        "total_wickets",
        "average",
        "strike_rate",
        "economy",
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
                        response.status_code,
                        500,
                        msg=f"{name}?sort={column} returned {response.status_code}",
                    )


class ThemeTemplateRegressionTests(TestCase):
    def test_records_page_section_headings_have_dark_mode_contrast_class(self):
        response = self.client.get(reverse("site-records"))

        self.assertEqual(response.status_code, 200)
        for heading in (
            "Highest Individual Scores",
            "Best Bowling Figures",
            "Most Runs in a Season",
            "Most Wickets in a Season",
            "Highest Team Totals",
        ):
            with self.subTest(heading=heading):
                self.assertContains(
                    response,
                    f'<h2 class="mb-4 text-xl font-bold text-ink-900 dark:text-ink-100">{heading}</h2>',
                    html=True,
                )

    def test_header_theme_toggle_stays_inside_responsive_header(self):
        response = self.client.get(reverse("site-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Toggle dark mode"')
        self.assertContains(response, "border border-ink-700 bg-ink-800 p-2 text-white")
        self.assertContains(response, "xl:flex")
        self.assertContains(response, "xl:hidden")
