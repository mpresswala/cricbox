from unfold.admin import ModelAdmin

from .models import Venue

from django.contrib import admin


# Register your models here.
class VenueAdmin(ModelAdmin):
    list_display = ["name", "location"]
    search_fields = ["name"]


admin.site.register(Venue, VenueAdmin)
