from datetime import date

from player.models import Player

from .models import Match, PlayerMatchAttribute

from django.test import TestCase
from django.urls import reverse


class AppearancesExcludesPseudoPlayersTests(TestCase):
    """The 'Extras'/'Unknown' pseudo-players must not appear in appearances,
    even when they have no last name (full name is 'Extras '), while a real
    player whose surname happens to be 'Unknown' is kept."""

    def setUp(self):
        real = Player.objects.create(first_name="Real", last_name="Player")
        real_unknown = Player.objects.create(first_name="Wayne", last_name="Unknown")
        extras = Player.objects.create(first_name="Extras")  # last_name is NULL
        unknown = Player.objects.create(first_name="Unknown")  # last_name is NULL
        match = Match.objects.create(date=date(2024, 5, 1))
        for player in (real, real_unknown, extras, unknown):
            PlayerMatchAttribute.objects.create(player=player, match=match)

    def test_pseudo_players_are_excluded(self):
        response = self.client.get(reverse("match-appearances-player"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Real Player")
        self.assertContains(response, "Wayne Unknown")  # real surname kept
        self.assertNotContains(response, "Extras")
