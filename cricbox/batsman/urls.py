from .views import BatsmanView, BatsmenView

from django.urls import path

urlpatterns = [
    # ex: /batting/
    path("stats/", BatsmenView.as_view(), name="batsmen-stats"),
    path("<int:id>/", BatsmanView.as_view(), name="batsman-stats"),
]
