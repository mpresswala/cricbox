# Cricbox imports
from cricbox.utils import FIFTIES, HUNDREDS
from match_statistics.models import MatchStatistics
from player.models import Player

# Django imports
from django.db import models
from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Max,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Concat


class Statistics(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(player__first_name="Extras")
            .values(
                "player_id",
                player_full_name=Concat("player__first_name", Value(" "), "player__last_name"),
            )
            .annotate(
                innings=Count("match_statistics") - Count("how_out", filter=Q(how_out__name="Did Not Bat")) - Count("how_out", filter=Q(how_out__name="Unknown")) ,
                runs_scored=Sum("runs"),
                not_out=Count("how_out", filter=Q(how_out__name="Not Out")),
                highest=Max("runs"),
                average=ExpressionWrapper(
                    F("runs_scored") / (F("innings") - F("not_out")),
                    output_field=DecimalField(max_digits=2, decimal_places=2),
                ),
                fifties=Count("runs", filter=FIFTIES),
                hundreds=Count("runs", filter=HUNDREDS),
            )
            .order_by("-runs_scored")
        )


class WicketType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "wicket_types"


class Batsman(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    scoring = models.CharField("Scoring", blank=True, max_length=200)
    runs = models.PositiveIntegerField("Runs", blank=True)
    how_out = models.ForeignKey(WicketType, blank=True, on_delete=models.PROTECT)
    bowler = models.CharField("Bowler", blank=True, max_length=25)

    match_statistics = models.ForeignKey(MatchStatistics, on_delete=models.PROTECT)
    objects = models.Manager()
    stat_objects = Statistics()

    class Meta:
        ordering = ["match_statistics__match__date"]
        verbose_name_plural = "Batsmen"
        db_table = "batsmen"

    def __str__(self):
        return self.player.full_name()
