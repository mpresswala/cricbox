from datetime import date

from match.models import HomeAway, Match, MatchType
from opposition.models import Opposition
from venue.models import Venue

from .models import MatchStatistics, Result

from django.test import TestCase
from django.urls import reverse


class OgImageTests(TestCase):
    """OG scorecard image generation."""

    def setUp(self):
        self.opposition = Opposition.objects.create(name="OG Test CC")
        self.venue = Venue.objects.create(name="OG Ground")
        self.home_away = HomeAway.objects.create(name="Home")
        self.match_type = MatchType.objects.create(name="League")
        self.won = Result.objects.create(name="Won")
        match = Match.objects.create(
            date=date(2025, 6, 15),
            season=2025,
            opposition=self.opposition,
            venue=self.venue,
            mtype=self.match_type,
            home_or_away=self.home_away,
        )
        self.ms = MatchStatistics.objects.create(
            match=match,
            result=self.won,
            london_fields_score=180,
            london_fields_wickets=6,
            london_fields_overs=35.4,
            opposition_score=142,
            opposition_wickets=8,
            opposition_overs=32.0,
            london_fields_first_event=0,
        )

    def test_og_image_returns_png(self):
        response = self.client.get(reverse("og-match-image", args=[self.ms.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_og_image_has_reasonable_size(self):
        response = self.client.get(reverse("og-match-image", args=[self.ms.id]))
        # Should be at least 5KB for a 1200x630 PNG
        self.assertGreater(len(response.content), 5000)

    def test_og_image_404_for_missing_match(self):
        response = self.client.get(reverse("og-match-image", args=[99999]))
        self.assertEqual(response.status_code, 404)


class SeasonOverviewAutocompleteFilterTests(TestCase):
    def setUp(self):
        self.alpha = Opposition.objects.create(name="Alpha CC")
        self.beta = Opposition.objects.create(name="Beta CC")
        self.main_ground = Venue.objects.create(name="Main Ground")
        self.away_ground = Venue.objects.create(name="Away Ground")
        self._match_stats(date(2024, 5, 1), self.alpha, self.main_ground)
        self._match_stats(date(2025, 5, 1), self.beta, self.away_ground)

    def _match_stats(self, match_date, opposition, venue):
        match = Match.objects.create(
            date=match_date,
            season=match_date.year,
            opposition=opposition,
            venue=venue,
        )
        return MatchStatistics.objects.create(match=match)

    def test_season_overview_has_opposition_and_venue_autocomplete_fields(self):
        response = self.client.get(reverse("season-overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="match__opposition__name__icontains"', html=False)
        self.assertContains(response, 'list="season-overview-opposition-options"', html=False)
        self.assertContains(response, '<option value="Alpha CC"></option>', html=True)
        self.assertContains(response, 'name="match__venue__name__icontains"', html=False)
        self.assertContains(response, 'list="season-overview-venue-options"', html=False)
        self.assertContains(response, '<option value="Main Ground"></option>', html=True)

    def test_season_overview_filters_by_typed_opposition_and_venue(self):
        response = self.client.get(
            reverse("season-overview"),
            {
                "match__opposition__name__icontains": "Alpha",
                "match__venue__name__icontains": "Main",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">2024</a>", html=False)
        self.assertNotContains(response, ">2025</a>", html=False)

    def test_opposition_overview_has_venue_autocomplete_and_filters(self):
        response = self.client.get(reverse("opposition-overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="match__venue__name__icontains"', html=False)
        self.assertContains(response, 'list="season-opposition-venue-options"', html=False)
        self.assertContains(response, '<option value="Main Ground"></option>', html=True)

        filtered = self.client.get(reverse("opposition-overview"), {"match__venue__name__icontains": "Main"})

        self.assertContains(filtered, "Alpha CC")
        self.assertNotContains(filtered, "Beta CC")

    def test_venues_overview_has_opposition_autocomplete_and_filters(self):
        response = self.client.get(reverse("venues-overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="match__opposition__name__icontains"', html=False)
        self.assertContains(response, 'list="season-venue-opposition-options"', html=False)
        self.assertContains(response, '<option value="Alpha CC"></option>', html=True)

        filtered = self.client.get(reverse("venues-overview"), {"match__opposition__name__icontains": "Alpha"})

        self.assertContains(filtered, "Main Ground")
        self.assertNotContains(filtered, "Away Ground")
