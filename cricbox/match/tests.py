from datetime import date

from opposition.models import Opposition
from player.models import Player
from venue.models import Venue

from .models import Match, PlayerMatchAttribute

from django.test import TestCase
from django.urls import reverse


class AppearancesExcludesPseudoPlayersTests(TestCase):
    """The 'Extras'/'Unknown' pseudo-players must not appear in appearances,
    even when they have no last name (full name is 'Extras '), while a real
    player whose surname happens to be 'Unknown' is kept."""

    def setUp(self):
        self.alpha = Opposition.objects.create(name="Alpha CC")
        self.beta = Opposition.objects.create(name="Beta CC")
        self.main_ground = Venue.objects.create(name="Main Ground")
        self.away_ground = Venue.objects.create(name="Away Ground")
        real = Player.objects.create(first_name="Real", last_name="Player")
        other = Player.objects.create(first_name="Other", last_name="Player")
        real_unknown = Player.objects.create(first_name="Wayne", last_name="Unknown")
        extras = Player.objects.create(first_name="Extras")  # last_name is NULL
        unknown = Player.objects.create(first_name="Unknown")  # last_name is NULL
        match = Match.objects.create(date=date(2024, 5, 1), opposition=self.alpha, venue=self.main_ground)
        other_match = Match.objects.create(date=date(2024, 5, 8), opposition=self.beta, venue=self.away_ground)
        for player in (real, real_unknown, extras, unknown):
            PlayerMatchAttribute.objects.create(player=player, match=match)
        PlayerMatchAttribute.objects.create(player=other, match=other_match)

    def test_pseudo_players_are_excluded(self):
        response = self.client.get(reverse("match-appearances-player"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Real Player")
        self.assertContains(response, "Wayne Unknown")  # real surname kept
        self.assertNotContains(response, "Extras")

    def test_autocomplete_filters_render_suggestions(self):
        response = self.client.get(reverse("match-appearances-player"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'list="appearances-opposition-options"', html=False)
        self.assertContains(response, '<option value="Alpha CC"></option>', html=True)
        self.assertContains(response, 'list="appearances-venue-options"', html=False)
        self.assertContains(response, '<option value="Main Ground"></option>', html=True)
        self.assertContains(response, 'list="appearances-player-options"', html=False)
        self.assertContains(response, '<option value="Real Player"></option>', html=True)
        self.assertNotContains(response, '<option value="Extras "></option>', html=True)

    def test_autocomplete_filters_limit_appearance_results(self):
        response = self.client.get(
            reverse("match-appearances-player"),
            {
                "opposition__name__icontains": "Alpha",
                "venue__name__icontains": "Main",
                "players__first_name__icontains": "Real",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td ><a href="/players/profiles/1/">Real Player</a></td>', html=True)
        self.assertNotContains(response, '<td ><a href="/players/profiles/2/">Other Player</a></td>', html=True)


class FixturesFilterTests(TestCase):
    def setUp(self):
        self.alpha = Opposition.objects.create(name="Alpha CC")
        self.beta = Opposition.objects.create(name="Beta CC")
        self.main_ground = Venue.objects.create(name="Main Ground")
        self.away_ground = Venue.objects.create(name="Away Ground")
        Match.objects.create(date=date(2024, 5, 1), opposition=self.alpha, venue=self.main_ground)
        Match.objects.create(date=date(2024, 5, 8), opposition=self.beta, venue=self.away_ground)

    def test_opposition_and_venue_filters_render_with_autocomplete_suggestions(self):
        response = self.client.get(reverse("fixtures-overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="opposition__name__icontains"', html=False)
        self.assertContains(response, 'list="fixtures-opposition-options"', html=False)
        self.assertContains(response, 'id="fixtures-opposition-options"', html=False)
        self.assertContains(response, '<option value="Alpha CC"></option>', html=True)
        self.assertContains(response, 'name="venue__name__icontains"', html=False)
        self.assertContains(response, 'list="fixtures-venue-options"', html=False)
        self.assertContains(response, 'id="fixtures-venue-options"', html=False)
        self.assertContains(response, '<option value="Main Ground"></option>', html=True)

    def test_opposition_and_venue_autocomplete_filters_limit_results(self):
        response = self.client.get(
            reverse("fixtures-overview"),
            {
                "opposition__name__icontains": "Alpha",
                "venue__name__icontains": "Main",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<td>Alpha CC</td>", html=True)
        self.assertContains(response, "<td>Main Ground</td>", html=True)
        self.assertNotContains(response, "<td>Beta CC</td>", html=True)
        self.assertNotContains(response, "<td>Away Ground</td>", html=True)
