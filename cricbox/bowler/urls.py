from .views import BowlersView, BowlerView

from django.urls import path

urlpatterns = [
    # ex: /bowling/
    path("stats/", BowlersView.as_view(), name="bowling-stats-all"),
    path("<int:id>/", BowlerView.as_view(), name="bowling-stats-name"),
]
