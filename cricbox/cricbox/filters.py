# Django third party apps
import django_filters


class MatchFilter(django_filters.FilterSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters["match_statistics__match__season__icontains"].label = "Year"
        self.filters["match_statistics__match__mtype"].label = "Type"
