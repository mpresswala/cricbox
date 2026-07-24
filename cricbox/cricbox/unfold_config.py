"""Shared django-unfold configuration.

Imported by the settings modules so the admin branding stays consistent
across local, dev and production.
"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "London Fields CC Admin",
    "SITE_HEADER": "London Fields CC",
    "SITE_SUBHEADER": "Match & statistics administration",
    "SITE_SYMBOL": "sports_cricket",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "236 253 245",
            "100": "209 250 229",
            "200": "167 243 208",
            "300": "110 231 183",
            "400": "52 211 153",
            "500": "16 185 129",
            "600": "5 150 105",
            "700": "4 120 87",
            "800": "6 95 70",
            "900": "6 78 59",
            "950": "2 44 34",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Cricket"),
                "separator": True,
                "items": [
                    {
                        "title": _("Matches"),
                        "icon": "stadium",
                        "link": reverse_lazy("admin:match_match_changelist"),
                    },
                    {
                        "title": _("Match statistics"),
                        "icon": "scoreboard",
                        "link": reverse_lazy(
                            "admin:match_statistics_matchstatistics_changelist"
                        ),
                    },
                    {
                        "title": _("Players"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:player_player_changelist"),
                    },
                    {
                        "title": _("Oppositions"),
                        "icon": "shield",
                        "link": reverse_lazy(
                            "admin:opposition_opposition_changelist"
                        ),
                    },
                    {
                        "title": _("Venues"),
                        "icon": "place",
                        "link": reverse_lazy("admin:venue_venue_changelist"),
                    },
                ],
            },
            {
                "title": _("Administration"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
