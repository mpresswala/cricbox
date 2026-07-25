import datetime

from django.db import models


class PlayingRole(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "playing_roles"


class BattingStyle(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "batting_styles"


class BowlingStyle(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "bowling_styles"


class AppointmentType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "appointment_types"


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=80, null=True)
    member_since = models.DateField("Date Joined", null=True, blank=True)
    email = models.EmailField("Email", null=True, blank=True)
    playing_role = models.ForeignKey(PlayingRole, on_delete=models.PROTECT, null=True, blank=True)
    batting_style = models.ForeignKey(BattingStyle, on_delete=models.PROTECT, null=True, blank=True)
    bowling_style = models.ForeignKey(BowlingStyle, on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(blank=True, default=True)
    life_member = models.BooleanField(default=False)

    class Meta:
        ordering = ["last_name"]
        db_table = "players"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    YEARS = []
    for year in range(1997, datetime.datetime.now().year + 1):
        YEARS.append((year, year))

    name = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.PROTECT)
    season = models.IntegerField("Season", default=datetime.datetime.now().year, choices=YEARS)

    class Meta:
        ordering = ["-season"]
        db_table = "appointments"

    def __str__(self):
        return f"{self.name}-{self.appointment_type}"
