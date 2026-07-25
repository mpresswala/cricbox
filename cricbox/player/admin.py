from unfold.admin import ModelAdmin

from .models import (
    Appointment,
    AppointmentType,
    BattingStyle,
    BowlingStyle,
    Player,
    PlayingRole,
)

from django.contrib import admin


# Register your models here.
class PlayingRoleAdmin(ModelAdmin):
    pass


class BattingStyleAdmin(ModelAdmin):
    pass


class BowlingStyleAdmin(ModelAdmin):
    pass


class AppointmentTypeAdmin(ModelAdmin):
    pass


class PlayerAdmin(ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "member_since",
        "playing_role",
        "batting_style",
        "bowling_style",
        "life_member",
    ]
    search_fields = ["first_name", "last_name"]
    list_filter = ["playing_role", "batting_style", "bowling_style", "life_member"]


class AppointmentAdmin(ModelAdmin):
    list_display = ["name", "appointment_type", "season"]
    search_fields = ["name__full_name", "season"]
    list_filter = ["appointment_type"]


admin.site.register(Player, PlayerAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(PlayingRole, PlayingRoleAdmin)
admin.site.register(BattingStyle, BattingStyleAdmin)
admin.site.register(BowlingStyle, BowlingStyleAdmin)
admin.site.register(AppointmentType, AppointmentTypeAdmin)
