# Cricbox imports
from match_statistics.models import MatchStatistics
from player.models import Player

# Django imports
from django.db import models
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db.models.functions import Concat


# class based model manager
class Statistics(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .values("player_id", player_full_name=Concat("player__first_name", Value(" "), "player__last_name"))
            .annotate(
                overs=Sum("overs"),
                maidens=Sum("maidens"),
                runs=Sum("runs"),
                total_wickets=Sum("wickets"),
                average=ExpressionWrapper(
                    F("runs") / F("total_wickets"),
                    output_field=DecimalField(max_digits=2, decimal_places=2),
                ),
                strike_rate=ExpressionWrapper(
                    F("overs") * 6 / F("total_wickets"),
                    output_field=DecimalField(max_digits=2, decimal_places=2),
                ),
                economy=ExpressionWrapper(
                    F("runs") / F("overs"),
                    output_field=DecimalField(max_digits=2, decimal_places=2),
                ),
                matches=Count("match_statistics"),
                fours=Count("wickets", Q(wickets=4)),
                fives=Count("wickets", Q(wickets__gt=4)),
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
        Returns the bowler's strike rate per match.
        :return: float or None when no wickets were taken
        """
        if not self.wickets:
            return None
        return round(self.overs * 6 / self.wickets, 2)

    @property
    def economy(self):
        """
        Returns the bowler's economy rate per match.
        :return: float or None when no overs were bowled
        """
        if not self.overs:
            return None
        return round(self.runs / self.overs, 2)

    def __str__(self):
        return self.player.full_name()
