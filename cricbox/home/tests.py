from datetime import date

from match.models import HomeAway, Match, MatchType
from match_statistics.models import MatchStatistics, Result
from opposition.models import Opposition
from venue.models import Venue

from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

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


class MarkdownFilterTests(TestCase):
    """home_extras templatetag: markdownify filter."""

    def test_markdownify_renders_bold(self):
        from home.templatetags.home_extras import markdownify
        result = markdownify("**bold text**")
        self.assertIn("<strong>bold text</strong>", result)

    def test_markdownify_renders_headings(self):
        from home.templatetags.home_extras import markdownify
        result = markdownify("# Heading 1\n\n## Heading 2")
        self.assertIn("<h1>Heading 1</h1>", result)
        self.assertIn("<h2>Heading 2</h2>", result)

    def test_markdownify_renders_code(self):
        from home.templatetags.home_extras import markdownify
        result = markdownify("Inline `code`")
        self.assertIn("<code>code</code>", result)

    def test_markdownify_renders_fenced_code_block(self):
        from home.templatetags.home_extras import markdownify
        result = markdownify("```\nprint('hello')\n```")
        self.assertIn("print", result)
        self.assertIn("code", result)

    def test_markdownify_returns_empty_string_for_none(self):
        from home.templatetags.home_extras import markdownify
        self.assertEqual(markdownify(None), "")
        self.assertEqual(markdownify(""), "")

    def test_markdownify_renders_tables(self):
        from home.templatetags.home_extras import markdownify
        result = markdownify("| A | B |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<table>", result)
        self.assertIn("<td>1</td>", result)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class OnThisDayTests(TestCase):
    """Homepage 'On This Day' widget."""

    def setUp(self):
        self.opposition = Opposition.objects.create(name="Test CC")
        self.venue = Venue.objects.create(name="Test Ground")
        self.home_away = HomeAway.objects.create(name="Home")
        self.match_type = MatchType.objects.create(name="Friendly")
        self.won = Result.objects.create(name="Won")
        self.today = timezone.now().date()

    def _match(self, match_date):
        match = Match.objects.create(
            date=match_date,
            season=match_date.year,
            opposition=self.opposition,
            venue=self.venue,
            mtype=self.match_type,
            home_or_away=self.home_away,
        )
        return MatchStatistics.objects.create(
            match=match,
            result=self.won,
            london_fields_score=150,
            london_fields_wickets=5,
        )

    def test_on_this_day_shows_historical_matches(self):
        self._match(date(self.today.year - 1, self.today.month, self.today.day))

        response = self.client.get(reverse("site-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "On This Day in LFCC History")
        self.assertContains(response, "Test CC")

    def test_on_this_day_hides_when_no_matches(self):
        response = self.client.get(reverse("site-home"))
        self.assertNotContains(response, "On This Day in LFCC History")

    def test_on_this_day_excludes_current_year(self):
        self._match(self.today)

        response = self.client.get(reverse("site-home"))
        self.assertNotContains(response, "On This Day in LFCC History")

    def test_on_this_day_uses_fixed_date(self):
        """Use a fixed date to avoid today() dependency."""
        ms = self._match(date(2025, 7, 15))
        now = self.today
        matches = type(ms).objects.filter(
            match__date__month=7,
            match__date__day=15,
            match__date__year__lt=now.year,
        )
        self.assertEqual(matches.count(), 1)
