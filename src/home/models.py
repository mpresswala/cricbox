from django.db import models
from player.models import Player
from match.models import Match

# Create your models here.
class NewsItem(models.Model):
    date = models.DateTimeField()
    text = models.CharField(max_length=300)

    class Meta:
        ordering = ["date"]
        db_table = "news_items"

    def __str__(self):
        return self.text


class Podcast(models.Model):
    title = models.TextField(max_length=20)
    url = models.URLField()
    date = models.DateTimeField()
    player = models.ManyToManyField(Player)

    class Meta:
        ordering = ["date"]
        db_table = "podcasts"

    def __str__(self):
        return self.title


class Picture(models.Model):
    title = models.TextField(max_length=20)
    date = models.PositiveIntegerField()
    match = models.ForeignKey(Match, null=True, on_delete=models.PROTECT)
    upload_date = models.DateTimeField()
    player = models.ManyToManyField(Player)

    class Meta:
        ordering = ["date"]
        db_table = "pictures"

    def __str__(self):
        return self.title
