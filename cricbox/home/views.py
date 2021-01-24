# Standard imports
import datetime

# Cricbox imports
from batsman.models import Batsman
from bowler.models import Bowler
from cricbox.utils import FIFTIES, FIVERS, HUNDREDS, SITE_URLS
from player.models import Appointment, Player

from .tables import (
    BestPlayer,
    HonoursTable,
    NotablePerformancesTable,
    Scorecard,
    VeteransTable,
)

# Django imports
from django.shortcuts import render
from django.views.generic import TemplateView

# Django third party apps
from django_tables2.views import MultiTableMixin


# Create your views here.
def home(request):
    return render(request, "home/home.html", context=SITE_URLS)


def stats(request):
    return render(request, "home/stats.html")


def history(request):
    london_fields_scorecard = [
        {
            "name": "Osman",
            "first_innings": "5 b. Ripley",
            "second_innings": "6 c. Erwood",
        },
        {
            "name": "Chapman",
            "first_innings": "2 b. Ripley",
            "second_innings": "0 b. Ripley",
        },
        {
            "name": "Barber",
            "first_innings": "0 b. Ripley",
            "second_innings": "5 b. Jonson",
        },
        {
            "name": "James",
            "first_innings": "2 stumpt Trigg",
            "second_innings": "10 b. Ripley",
        },
        {
            "name": "Burrow",
            "first_innings": "0 st. Messenger",
            "second_innings": "6 c. Erwood",
        },
        {
            "name": "Lorimer",
            "first_innings": "3 b. Messenger",
            "second_innings": "5 c. Jonson",
        },
        {
            "name": "Pearce",
            "first_innings": "25 not out",
            "second_innings": "10 b. Ripley",
        },
        {
            "name": "Large",
            "first_innings": "1 b. Ripley",
            "second_innings": "6 c. Jonson",
        },
        {
            "name": "Low",
            "first_innings": "3 b. Ripley",
            "second_innings": "2 stumpt Ripley",
        },
        {
            "name": "Hoare",
            "first_innings": "4 b. Crisford",
            "second_innings": "1 run out",
        },
        {
            "name": "Yeats",
            "first_innings": "0 b. Messenger",
            "second_innings": "7 not out",
        },
        {"name": "Extras", "first_innings": "Byes 2", "second_innings": "Byes 3"},
        {"name": "Total", "first_innings": "47", "second_innings": "53"},
    ]
    clapton_scorecard = [
        {"name": "Glaizer", "first_innings": "16 b. Pearce"},
        {"name": "Robbin", "first_innings": "18 c. Lorimer"},
        {"name": "Hoare", "first_innings": "1 stumpt Barber"},
        {"name": "Jonson", "first_innings": "45 stumpt Osman"},
        {"name": "Messenger", "first_innings": "13 c. ditto"},
        {"name": "Prise", "first_innings": "21 c. Yeats"},
        {"name": "Crisford", "first_innings": "13 b. Pearce"},
        {"name": "Ripley", "first_innings": "4 b. Osman"},
        {"name": "Stewart", "first_innings": "2 c. Hoare"},
        {"name": "Jaines", "first_innings": "not out"},
        {"name": "Smith", "first_innings": "2 c. Osman"},
        {"name": "Extras", "first_innings": "Byes 11"},
        {"name": "Total", "first_innings": "149"},
    ]
    tables = [
        Scorecard(london_fields_scorecard),
        Scorecard(clapton_scorecard, exclude="second_innings"),
    ]

    return render(request, "home/history.html", {"tables": tables})


def about(request):
    return render(request, "home/about.html", context=SITE_URLS)


def links(request):
    return render(request, "home/links.html")


class PositionsView(MultiTableMixin, TemplateView):
    template_name = "home/club_positions.html"
    table_pagination = {"per_page": 50}

    def get_tables(self):
        return [
            HonoursTable(Appointment.objects.filter(appointment_type__name="Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="Vice Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="MidWeek Captain").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type__name="Fixturer").order_by("-season")),
            HonoursTable(
                Appointment.objects.filter(appointment_type__name="Domestic Tour Secretary").order_by("-season")
            ),
            HonoursTable(
                Appointment.objects.filter(appointment_type__name="International Tour Secretary").order_by("-season")
            ),
            VeteransTable(
                Player.objects.filter(member_since__year=datetime.datetime.now().year - 10),
                order_by="-member_since__year",
            ),
        ]


class PerformersView(MultiTableMixin, TemplateView):
    template_name = "home/club_performers.html"
    table_pagination = {"per_page": 50}

    best_batsman_query = """
        SELECT id, name, batsmen_all_seasons.season, total
        FROM (
                SELECT season, max(total) as max_total
                FROM batsmen_all_seasons
                GROUP BY season
            ) AS max_per_season
            inner join batsmen_all_seasons
                ON batsmen_all_seasons.season = max_per_season.season AND max_per_season.max_total = batsmen_all_seasons.total
        ORDER BY batsmen_all_seasons.season DESC;
    """

    best_bowler_query = """
        SELECT id, name, bowler_all_seasons.season, total
        FROM (
                SELECT season, max(total) as max_total
                FROM bowler_all_seasons
                GROUP BY season
            ) AS max_per_season
            inner join bowler_all_seasons
                ON bowler_all_seasons.season = max_per_season.season and max_per_season.max_total = bowler_all_seasons.total
        ORDER BY bowler_all_seasons.season DESC;
    """

    def get_tables(self):
        return [
            NotablePerformancesTable(
                Batsman.objects.filter(FIFTIES).order_by("-match_statistics__match__season"),
                exclude="wickets",
            ),
            NotablePerformancesTable(
                Batsman.objects.filter(HUNDREDS).order_by("-match_statistics__match__season"),
                exclude="wickets",
            ),
            NotablePerformancesTable(
                Bowler.objects.filter(FIVERS).order_by("-match_statistics__match__season"),
                exclude="runs",
            ),
            BestPlayer(Batsman.objects.raw(self.best_batsman_query)),
            BestPlayer(Bowler.objects.raw(self.best_bowler_query)),
        ]


def handbook(request):
    return render(request, "home/handbook.html", SITE_URLS)


def match_manager(request):
    return render(request, "home/match_manager.html")
