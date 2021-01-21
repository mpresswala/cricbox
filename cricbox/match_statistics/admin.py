from django.contrib import admin
from .models import MatchStatistics, Result
from batsman.models import Batsman
from bowler.models import Bowler

# Register your models here
class ResultAdmin(admin.ModelAdmin):
    pass


class BatsmanAdmin(admin.TabularInline):
    model = Batsman


class BowlerAdmin(admin.TabularInline):
    model = Bowler


class MatchStatisticsAdmin(admin.ModelAdmin):
    list_display = ("opposition", "date", "venue", "mtype", "result")
    list_filter = ["match__date", "match__mtype", "match__home_or_away", "result"]
    date_hierarchy = "match__date"
    inlines = (BatsmanAdmin, BowlerAdmin)

    def date(self, x):
        return x.match.date

    def opposition(self, x):
        return x.match.opposition.name

    def venue(self, x):
        return x.match.venue.name

    def mtype(self, x):
        return x.match.mtype.name

    mtype.short_description = "Type"


admin.site.register(Result, ResultAdmin)

admin.site.register(MatchStatistics, MatchStatisticsAdmin)
