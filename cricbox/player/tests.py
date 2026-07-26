from datetime import date
from decimal import Decimal

from batsman.models import Batsman, WicketType
from bowler.models import Bowler
from match.models import Match, PlayerMatchAttribute
from match_statistics.models import MatchStatistics

from .models import Player
from .views import _appearance_count, _parse_from_date, _parse_player_id, _player_summary

from django.test import TestCase
from django.urls import reverse


class PlayerCompareHelperTests(TestCase):
    def setUp(self):
        self.caught = WicketType.objects.create(name="Caught")
        self.alice = Player.objects.create(first_name="Alice", last_name="Batter")
        self.bob = Player.objects.create(first_name="Bob", last_name="Bowler")

    def _match(self, match_date):
        match = Match.objects.create(date=match_date, season=match_date.year)
        return match, MatchStatistics.objects.create(match=match)

    def _batting_row(self, player, match_date, runs=10):
        stats = self._match(match_date)[1]
        return Batsman.objects.create(player=player, match_statistics=stats, how_out=self.caught, runs=runs)

    def _bowling_row(self, player, match_date, overs=Decimal("3.0"), runs=12, wickets=2):
        stats = self._match(match_date)[1]
        return Bowler.objects.create(
            player=player,
            match_statistics=stats,
            overs=overs,
            runs=runs,
            wickets=wickets,
        )

    def test_parse_from_date_handles_valid_empty_and_invalid_values(self):
        self.assertEqual(_parse_from_date("2024-01-31"), date(2024, 1, 31))
        self.assertIsNone(_parse_from_date(""))
        self.assertIsNone(_parse_from_date("2024-99-99"))

    def test_parse_player_id_handles_valid_and_invalid_values(self):
        self.assertEqual(_parse_player_id(str(self.alice.pk)), self.alice.pk)
        self.assertIsNone(_parse_player_id(""))
        self.assertIsNone(_parse_player_id("not-a-number"))

    def test_appearance_count_uses_match_links_and_scorecard_rows_after_date(self):
        old_match, old_stats = self._match(date(2023, 8, 1))
        Batsman.objects.create(player=self.alice, match_statistics=old_stats, how_out=self.caught, runs=99)
        PlayerMatchAttribute.objects.create(player=self.alice, match=old_match)

        linked_match = self._match(date(2024, 5, 1))[0]
        PlayerMatchAttribute.objects.create(player=self.alice, match=linked_match)

        scorecard_stats = self._match(date(2024, 6, 1))[1]
        Batsman.objects.create(player=self.alice, match_statistics=scorecard_stats, how_out=self.caught, runs=25)
        Bowler.objects.create(
            player=self.alice,
            match_statistics=scorecard_stats,
            overs=Decimal("4.0"),
            runs=20,
            wickets=1,
        )

        self.assertEqual(_appearance_count(self.alice.pk, date(2024, 1, 1)), 2)
        self.assertEqual(_appearance_count(self.alice.pk), 3)

    def test_player_summary_applies_from_date_to_all_stat_sections(self):
        self._batting_row(self.alice, date(2023, 7, 1), runs=100)
        self._batting_row(self.alice, date(2024, 7, 1), runs=40)
        self._bowling_row(self.alice, date(2024, 7, 2), overs=Decimal("3.0"), runs=12, wickets=2)

        summary = _player_summary(self.alice.pk, date(2024, 1, 1))
        if summary is None:
            self.fail("Expected an existing player summary")

        self.assertEqual(summary["appearances"], 2)
        self.assertEqual(summary["batting"]["innings"], 1)
        self.assertEqual(summary["batting"]["runs_scored"], 40)
        self.assertEqual(summary["bowling"]["overs"], 3)
        self.assertEqual(summary["bowling"]["total_wickets"], 2)

    def test_player_summary_returns_none_for_unknown_player(self):
        self.assertIsNone(_player_summary(999999))


class PlayerCompareViewTests(TestCase):
    def setUp(self):
        self.caught = WicketType.objects.create(name="Caught")
        self.alice = Player.objects.create(first_name="Alice", last_name="Batter")
        self.bob = Player.objects.create(first_name="Bob", last_name="Bowler")

    def _match_stats(self, match_date):
        match = Match.objects.create(date=match_date, season=match_date.year)
        return MatchStatistics.objects.create(match=match)

    def test_compare_page_renders_selected_players_and_from_date_stats(self):
        alice_stats = self._match_stats(date(2024, 5, 1))
        bob_stats = self._match_stats(date(2024, 5, 2))
        Batsman.objects.create(player=self.alice, match_statistics=alice_stats, how_out=self.caught, runs=30)
        Bowler.objects.create(
            player=self.bob,
            match_statistics=bob_stats,
            overs=Decimal("2.0"),
            runs=8,
            wickets=3,
        )

        response = self.client.get(
            reverse("player-compare"),
            {"a": self.alice.pk, "b": self.bob.pk, "from_date": "2024-01-01"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Showing stats from 1 January 2024")
        self.assertContains(response, "Alice Batter")
        self.assertContains(response, "Bob Bowler")
        self.assertContains(response, "<td>1</td>", html=True)

    def test_compare_page_ignores_invalid_from_date_without_crashing(self):
        response = self.client.get(
            reverse("player-compare"),
            {"a": self.alice.pk, "b": self.bob.pk, "from_date": "2024-99-99"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Showing stats from")


class PlayerSearchViewTests(TestCase):
    def _report(self, headline, report_text=""):
        match = Match.objects.create(date=date(2024, 6, 1), season=2024)
        return MatchStatistics.objects.create(match=match, report_headline=headline, report=report_text)

    def test_player_search_filters_matches_and_excludes_pseudo_players(self):
        Player.objects.create(first_name="Alice", last_name="Batter")
        Player.objects.create(first_name="Bob", last_name="Bowler")
        Player.objects.create(first_name="Extras", last_name="")

        response = self.client.get(reverse("player-search"), {"q": "ali"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Batter")
        self.assertNotContains(response, "Bob Bowler")
        self.assertNotContains(response, "Extras")

    def test_player_search_includes_matching_match_reports(self):
        report = self._report("Derby day thriller", "A tense final over report.")
        self._report("Routine league win", "Nothing about the searched term.")

        response = self.client.get(reverse("player-search"), {"q": "thriller"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Match reports")
        self.assertContains(response, "Derby day thriller")
        self.assertContains(response, reverse("match-overview", args=[report.pk]))
        self.assertNotContains(response, "Routine league win")

    def test_player_search_can_match_report_body_text(self):
        self._report("A quiet headline", "Late wickets turn the contest.")

        response = self.client.get(reverse("player-search"), {"q": "wickets"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A quiet headline")

    def test_player_search_empty_query_returns_no_results(self):
        Player.objects.create(first_name="Alice", last_name="Batter")
        self._report("Derby day thriller")

        response = self.client.get(reverse("player-search"), {"q": ""})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Alice Batter")
        self.assertNotContains(response, "Derby day thriller")

    def test_player_search_empty_state_mentions_players_and_reports(self):
        response = self.client.get(reverse("player-search"), {"q": "missing"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No players or match reports found.")
