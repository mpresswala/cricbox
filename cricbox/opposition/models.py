from django.db import models


# Create your models here.
class Opposition(models.Model):
    name = models.CharField(max_length=50)
    site = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        db_table = "oppositions"

    def __str__(self):
        return self.name
