from datetime import date

from match.models import Match
from opposition.models import Opposition
from venue.models import Venue

from .models import MatchStatistics

from django.test import TestCase
from django.urls import reverse


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
