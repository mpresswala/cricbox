# Cricbox imports
# Third-party imports
from unfold.admin import ModelAdmin

from home.models import ClubDocument, NewsItem, Picture, Podcast

# Django imports
from django.contrib import admin


# Register your models here.
class NewsAdmin(ModelAdmin):
    model = NewsItem


class PodcastAdmin(ModelAdmin):
    model = Podcast


class PicturesAdmin(ModelAdmin):
    model = Picture


class DocumentsAdmin(ModelAdmin):
    model = ClubDocument


admin.site.register(NewsItem, NewsAdmin)
admin.site.register(Podcast, PodcastAdmin)
admin.site.register(Picture, PicturesAdmin)
admin.site.register(ClubDocument, DocumentsAdmin)
