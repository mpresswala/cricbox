# Django imports
from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "yearly"

    def items(self):
        return [
            "site-home",
            "site-about",
            "site-history",
            "site-links",
            "site-handbook",
            "site-match_manager",
        ]

    def location(self, item):
        return reverse(item)
