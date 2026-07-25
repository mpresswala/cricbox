from django.db import models


# Create your models here.
class Venue(models.Model):
    name = models.CharField(max_length=50)
    location = models.URLField("Map link to the venue", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        db_table = "venues"

    def __str__(self):
        return self.name
