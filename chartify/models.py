from django.db import models


class Track(models.Model):
    track_id = models.CharField(max_length=16, primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    img_url = models.URLField(null=True, blank=True)
    spot_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["track_id"]

    def __str__(self):
        return self.name


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=255, primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    track = models.ManyToManyField(Track, related_name="playlists")
    # last_chart_id = models.CharField(max_length=20, null=True)

    class Meta:
        ordering = ["playlist_id"]

    def __str__(self):
        return self.name
