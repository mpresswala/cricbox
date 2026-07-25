from cricbox.utils import BALLS_PER_OVER, overs_to_balls
from match_statistics.models import MatchStatistics
from player.models import Player

from django.db import models
from django.db.models import Count, DecimalField, ExpressionWrapper, F, IntegerField, Q, Sum, Value
from django.db.models.functions import Concat, Floor, NullIf


# class based model manager
class Statistics(models.Manager):
    def get_queryset(self):
        # Overs are base-6 (4.3 == 4 overs 3 balls), so they cannot be summed as
        # decimals. Convert each innings to balls, total those, and derive the
        # bowling figures from the ball count.
        balls = ExpressionWrapper(
            Floor(F("overs")) * BALLS_PER_OVER + (F("overs") - Floor(F("overs"))) * 10,
            output_field=IntegerField(),
        )
        return (
            super()
            .get_queryset()
            .exclude(player__first_name="Extras")
            .values("player_id", player_full_name=Concat("player__first_name", Value(" "), "player__last_name"))
            .annotate(
                total_balls=Sum(balls),
                maidens=Sum("maidens"),
                runs=Sum("runs"),
                total_wickets=Sum("wickets"),
                matches=Count("match_statistics"),
                fours=Count("wickets", Q(wickets=4)),
                fives=Count("wickets", Q(wickets__gt=4)),
            )
            .annotate(
                average=ExpressionWrapper(
                    F("runs") / NullIf(F("total_wickets"), 0),
                    output_field=DecimalField(max_digits=6, decimal_places=2),
                ),
                strike_rate=ExpressionWrapper(
                    F("total_balls") * Value(1.0) / NullIf(F("total_wickets"), 0),
                    output_field=DecimalField(max_digits=6, decimal_places=2),
                ),
                economy=ExpressionWrapper(
                    F("runs") * Value(float(BALLS_PER_OVER)) / NullIf(F("total_balls"), 0),
                    output_field=DecimalField(max_digits=6, decimal_places=2),
                ),
            )
            .order_by("-total_wickets")
        )


class Bowler(models.Model):
    number = models.PositiveSmallIntegerField("Bowler Number", blank=True, default=0)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    overs = models.DecimalField("Overs", max_digits=3, decimal_places=1, default=0)
    maidens = models.PositiveIntegerField("Maidens", blank=True, default=0)
    runs = models.PositiveIntegerField("Runs", default=0)
    wickets = models.PositiveIntegerField("Wickets", default=0)
    match_statistics = models.ForeignKey(MatchStatistics, on_delete=models.PROTECT)
    objects = models.Manager()
    stat_objects = Statistics()

    class Meta:
        ordering = ["player"]
        db_table = "bowlers"

    @property
    def figures(self):
        """Bowling figures for the innings, e.g. '8/11' (wickets/runs)."""
        return f"{self.wickets}/{self.runs}"

    @property
    def average(self):
        """
        Returns the bowler's average per match.
        :return: float or None when no wickets were taken
        """
        if not self.wickets:
            return None
        return round(self.runs / self.wickets, 2)

    @property
    def strike_rate(self):
        """
        Returns the bowler's strike rate (balls per wicket).
        :return: float or None when no wickets were taken
        """
        if not self.wickets:
            return None
        return round(overs_to_balls(self.overs) / self.wickets, 2)

    @property
    def economy(self):
        """
        Returns the bowler's economy rate (runs per over).
        :return: float or None when no overs were bowled
        """
        balls = overs_to_balls(self.overs)
        if not balls:
            return None
        return round(self.runs / (balls / BALLS_PER_OVER), 2)

    def __str__(self):
        return self.player.full_name()
