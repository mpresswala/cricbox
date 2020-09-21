from django.shortcuts import render
from .tables import Scorecard, HonoursTable, NotablePerformancesTable, VeteransTable
from london_fields.utils import SITE_URLS, FIFTIES, HUNDREDS, FIVERS
from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from player.models import Appointment
from batsman.models import Batsman
from bowler.models import Bowler
from player.models import Player
import datetime

# Create your views here.
def home(request):
    return render(request, "home/home.html", context=SITE_URLS)


def stats(request):
    return render(request, "home/stats.html")


def history(request):
    london_fields_scorecard = [
        {"name": "Osman", "first_innings": "5 b. Ripley", "second_innings": "6 c. Erwood"},
        {"name": "Chapman", "first_innings": "2 b. Ripley", "second_innings": "0 b. Ripley"},
        {"name": "Barber", "first_innings": "0 b. Ripley", "second_innings": "5 b. Jonson"},
        {"name": "James", "first_innings": "2 stumpt Trigg", "second_innings": "10 b. Ripley"},
        {"name": "Burrow", "first_innings": "0 st. Messenger", "second_innings": "6 c. Erwood"},
        {"name": "Lorimer", "first_innings": "3 b. Messenger", "second_innings": "5 c. Jonson"},
        {"name": "Pearce", "first_innings": "25 not out", "second_innings": "10 b. Ripley"},
        {"name": "Large", "first_innings": "1 b. Ripley", "second_innings": "6 c. Jonson"},
        {"name": "Low", "first_innings": "3 b. Ripley", "second_innings": "2 stumpt Ripley"},
        {"name": "Hoare", "first_innings": "4 b. Crisford", "second_innings": "1 run out"},
        {"name": "Yeats", "first_innings": "0 b. Messenger", "second_innings": "7 not out"},
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
        {"name": "Total", "first_innings": "149"}
        ]
    tables = [
        Scorecard(london_fields_scorecard),
        Scorecard(clapton_scorecard, exclude="second_innings")
        ]

    return render(request, "home/history.html", {"tables": tables})


def about(request):
    return render(request, "home/about.html", context=SITE_URLS)


def links(request):
    return render(request, "home/links.html")


class HonoursView(MultiTableMixin, TemplateView):
    template_name = "home/honours.html"
    table_pagination = {
        "per_page": 50
        }

    def get_tables(self):
        return [
            HonoursTable(Appointment.objects.filter(appointment_type="CAP").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type="VCAP").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type="MCAP").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type="FIX").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type="DTOUR").order_by("-season")),
            HonoursTable(Appointment.objects.filter(appointment_type="ITOUR").order_by("-season")),
            VeteransTable(Player.objects.filter(member_since__year=datetime.datetime.now().year - 10),
                          order_by="-member_since__year"),
            NotablePerformancesTable(Batsman.objects.filter(FIFTIES).order_by("-match_statistics__match__season"),
                                     exclude="wickets"),
            NotablePerformancesTable(Batsman.objects.filter(HUNDREDS).order_by("-match_statistics__match__season"),
                                     exclude="wickets"),
            NotablePerformancesTable(Bowler.objects.filter(FIVERS).order_by("-match_statistics__match__season"),
                                     exclude="runs")
            ]


def handbook(request):
    return render(request, "home/handbook.html", SITE_URLS)


def match_manager(request):
    return render(request, "home/match_manager.html")
