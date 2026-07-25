# Cricbox imports
from match.models import Match

from .choices import EVENT_FIRST

# Django imports
from django.db import models


class Result(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "results"


class MatchStatistics(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, null=True)
    result = models.ForeignKey(Result, verbose_name="Result", on_delete=models.PROTECT, null=True)
    report = models.TextField("Report", blank=True, null=True)
    london_fields_overs = models.DecimalField("London Fields Overs Bowled", max_digits=3, decimal_places=1, null=True)
    london_fields_score = models.PositiveSmallIntegerField("London Fields Score", null=True)
    london_fields_wickets = models.PositiveSmallIntegerField("London Fields Wickets Taken", null=True)
    opposition_score = models.PositiveSmallIntegerField("Opposition score", null=True)
    opposition_wickets = models.PositiveSmallIntegerField("Opposition Wickets Taken", null=True)
    opposition_overs = models.DecimalField("Opposition overs Bowled", max_digits=3, decimal_places=1, null=True)
    london_fields_first_event = models.PositiveSmallIntegerField(choices=EVENT_FIRST, default=0, null=True)
    report_byline = models.CharField(max_length=200, null=True)
    report_author = models.CharField(max_length=200, null=True)
    report_headline = models.CharField(max_length=200, null=True)

    def get_bowlers(self):
        return self.bowler_set.get_queryset().order_by("number")

    def get_batsman(self):
        return self.batsman_set.get_queryset()

    class Meta:
        ordering = ("match",)
        db_table = "matches_statistics"
        verbose_name_plural = "Match Statistics"

    def __str__(self):
        return f"{self.match}"
