from match_statistics.models import MatchStatistics
from player.models import Player

from .models import Batsman, WicketType

from django.forms.models import modelform_factory
from django.test import TestCase

# Fields the admin inline exposes for a Batsman row.
BatsmanForm = modelform_factory(
    Batsman,
    fields=["player", "scoring", "runs", "how_out", "bowler", "match_statistics"],
)


class BatsmanFormValidationTests(TestCase):
    """
    Regression tests for the '500 error and all data is gone' bug.

    'runs' and 'how_out' were declared blank=True while the DB columns are
    NOT NULL with no default, so leaving them empty passed form validation
    and then raised IntegrityError at save() -> unhandled 500, losing every
    inline the user had typed. They must now fail validation gracefully.
    """

    def setUp(self):
        self.player = Player.objects.create(first_name="Joe", last_name="Bloggs")
        self.caught = WicketType.objects.create(name="Caught")
        self.match_statistics = MatchStatistics.objects.create()

    def _data(self, **overrides):
        data = {
            "player": str(self.player.id),
            "scoring": "",
            "runs": "10",
            "how_out": str(self.caught.id),
            "bowler": "",
            "match_statistics": str(self.match_statistics.id),
        }
        data.update(overrides)
        return data

    def test_blank_runs_is_a_validation_error_not_a_500(self):
        form = BatsmanForm(self._data(runs=""))
        self.assertFalse(form.is_valid())
        self.assertIn("runs", form.errors)

    def test_blank_how_out_is_a_validation_error_not_a_500(self):
        form = BatsmanForm(self._data(how_out=""))
        self.assertFalse(form.is_valid())
        self.assertIn("how_out", form.errors)

    def test_valid_row_still_saves(self):
        form = BatsmanForm(self._data())
        self.assertTrue(form.is_valid(), form.errors)
        batsman = form.save()
        self.assertEqual(batsman.runs, 10)
        self.assertEqual(batsman.how_out, self.caught)
