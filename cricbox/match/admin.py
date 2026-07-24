# Cricbox imports
from match.models import PlayerMatchAttribute

from .models import HomeAway, Match, MatchType, PlayerSkill

# Django imports
from django.contrib import admin

# Third-party imports
from unfold.admin import ModelAdmin, TabularInline


# Register your models here.
class MatchTypeAdmin(ModelAdmin):
    pass


class HomeAwayAdmin(ModelAdmin):
    pass


class PlayerSkillAdmin(ModelAdmin):
    pass


class PlayerInlineAdmin(TabularInline):
    model = PlayerMatchAttribute


class MatchAdmin(ModelAdmin):
    list_display = ("opposition", "date", "venue", "mtype")
    list_filter = ["date", "home_or_away", "mtype"]
    search_fields = ["opposition__name", "venue__name", "mtype"]
    inlines = (PlayerInlineAdmin,)
    date_hierarchy = "date"


admin.site.register(Match, MatchAdmin)
admin.site.register(MatchType, MatchTypeAdmin)
admin.site.register(PlayerSkill, PlayerSkillAdmin)
admin.site.register(HomeAway, HomeAwayAdmin)
