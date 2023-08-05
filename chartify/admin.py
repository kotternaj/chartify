from django.contrib import admin
from .models import *

# from dbApp.models import Person, City, Country


# class PlAdmin(admin.ModelAdmin):
#     list_display = ("name", "track")


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("playlist_id", "name")
    search_fields = ["playlist_id", "name"]
    list_filter = ("name",)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        "track_id",
        "name",
        "artist",
        "spot_id",
        "img_url",
    )
    # list_filter = ("artist",)
    search_fields = ["name", "artist", "track_id"]
