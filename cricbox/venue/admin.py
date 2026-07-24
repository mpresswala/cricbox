from .models import Venue

# Django imports
from django.contrib import admin

# Third-party imports
from unfold.admin import ModelAdmin


# Register your models here.
class VenueAdmin(ModelAdmin):
    list_display = ["name", "location"]
    search_fields = ["name"]


admin.site.register(Venue, VenueAdmin)
