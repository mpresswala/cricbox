from unfold.admin import ModelAdmin

from .models import Batsman, WicketType

from django.contrib import admin


# Register your models here.
class WicketTypeAdmin(ModelAdmin):
    pass


class BatsmanAdmin(ModelAdmin):
    list_display = ("player", "how_out", "bowler", "runs", "match_statistics")
    list_filter = ["how_out"]
    search_fields = ["player__full_name", "bowler"]


admin.site.register(Batsman, BatsmanAdmin)
admin.site.register(WicketType, WicketTypeAdmin)
