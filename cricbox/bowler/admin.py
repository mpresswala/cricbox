from .models import Bowler

# Django imports
from django.contrib import admin

# Third-party imports
from unfold.admin import ModelAdmin


# Register your models here.
class BowlerAdmin(ModelAdmin):
    list_display = ("player", "overs", "maidens", "runs", "wickets", "match_statistics")
    search_fields = ["player__full_name"]


admin.site.register(Bowler, BowlerAdmin)
