# Cricbox imports
from match_statistics.models import MatchStatistics
from player.models import Player

from .models import Bowler

# Django imports
from django.test import TestCase


class BowlerStatPropertyTests(TestCase):
    """
    Regression tests: average / strike_rate / economy used to raise
    ZeroDivisionError when a bowler took no wickets or bowled no overs.
    They now return None instead of crashing.
    """

    def setUp(self):
        self.player = Player.objects.create(first_name="Joe", last_name="Bloggs")
        self.match_statistics = MatchStatistics.objects.create()

    def _bowler(self, **kwargs):
        defaults = dict(
            number=1, player=self.player, overs=5, maidens=0, runs=20,
            wickets=2, match_statistics=self.match_statistics,
        )
        defaults.update(kwargs)
        return Bowler.objects.create(**defaults)

    def test_no_wickets_does_not_raise(self):
        bowler = self._bowler(wickets=0)
        self.assertIsNone(bowler.average)
        self.assertIsNone(bowler.strike_rate)

    def test_no_overs_does_not_raise(self):
        bowler = self._bowler(overs=0)
        self.assertIsNone(bowler.economy)

    def test_normal_figures_are_computed(self):
        bowler = self._bowler(overs=4, runs=24, wickets=2)
        self.assertEqual(bowler.average, 12)
        self.assertEqual(bowler.economy, 6)
        self.assertEqual(bowler.strike_rate, 12)
