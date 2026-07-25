import datetime

from opposition.models import Opposition
from player.models import Player
from venue.models import Venue

from django.db import models


# Create your models here.
class HomeAway(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "home_away"


class MatchType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "match_types"


class PlayerSkill(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "player_skills"


class Match(models.Model):
    YEARS = []
    for year in range(1997, datetime.datetime.now().year + 1):
        YEARS.append((year, year))

    season = models.IntegerField("Season", default=datetime.datetime.now().year, choices=YEARS)
    date = models.DateField("Date")
    mtype = models.ForeignKey(
        MatchType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Match Type",
    )
    home_or_away = models.ForeignKey(HomeAway, verbose_name="Home or Away", null=True, on_delete=models.PROTECT)
    remarks = models.CharField("Remarks", blank=True, max_length=200, default="")
    opposition = models.ForeignKey(Opposition, on_delete=models.PROTECT, blank=True, null=True)
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, blank=True, null=True)
    players = models.ManyToManyField(Player, blank=True, through="PlayerMatchAttribute")

    class Meta:
        ordering = ["-season", "date"]
        verbose_name_plural = "matches"
        db_table = "matches"

    def __str__(self):
        return f"London Fields vs {self.opposition} at {self.venue}, {self.date.strftime('%d %b, %Y')}"

    def get_absolute_url(self):
        return f"/season/match/{self.id}"


class PlayerMatchAttribute(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True)
    skill = models.ForeignKey(PlayerSkill, null=True, verbose_name="Skill Set", on_delete=models.PROTECT)
    captain = models.BooleanField("Captain", default=False, null=True)

    class Meta:
        db_table = "player_match_attributes"

    def __str__(self):
        return f"{self.skill}"
