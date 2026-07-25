# Cricbox imports
# Third-party imports
from unfold.admin import ModelAdmin, TabularInline

from batsman.models import Batsman
from bowler.models import Bowler

from .models import MatchStatistics, Result

# Django imports
from django.contrib import admin


# Register your models here
class ResultAdmin(ModelAdmin):
    pass


class BatsmanAdmin(TabularInline):
    model = Batsman
    autocomplete_fields = ["player"]


class BowlerAdmin(TabularInline):
    model = Bowler
    autocomplete_fields = ["player"]


class MatchStatisticsAdmin(ModelAdmin):
    list_display = ("opposition", "date", "venue", "mtype", "result")
    list_filter = ["match__date", "match__mtype", "match__home_or_away", "result"]
    date_hierarchy = "match__date"
    inlines = (BatsmanAdmin, BowlerAdmin)
    # autocomplete_fields = ["batsman__player", "bowler__player"]

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
