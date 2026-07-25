from unfold.admin import ModelAdmin, TabularInline

from batsman.models import Batsman
from bowler.models import Bowler

from .models import MatchStatistics, Result

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

    @admin.display(description="Date")
    def date(self, obj):
        return obj.match.date if obj.match else ""

    @admin.display(description="Opposition")
    def opposition(self, obj):
        if obj.match and obj.match.opposition:
            return obj.match.opposition.name
        return ""

    @admin.display(description="Venue")
    def venue(self, obj):
        if obj.match and obj.match.venue:
            return obj.match.venue.name
        return ""

    @admin.display(description="Type")
    def mtype(self, obj):
        if obj.match and obj.match.mtype:
            return obj.match.mtype.name
        return ""


admin.site.register(Result, ResultAdmin)

admin.site.register(MatchStatistics, MatchStatisticsAdmin)
