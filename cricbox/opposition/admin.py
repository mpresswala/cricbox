# Third-party imports
from unfold.admin import ModelAdmin

from .models import Opposition

# Django imports
from django.contrib import admin


# Register your models here.
class OppositionAdmin(ModelAdmin):
    list_display = ["name", "site"]
    search_fields = ["name"]


admin.site.register(Opposition, OppositionAdmin)
