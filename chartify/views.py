from django.http import JsonResponse
from django.shortcuts import render
import random, json
from .login import login
from .models import Playlist, Track


def random_chart(request):
    playlists = Playlist.objects.all()
    tracks = Track.objects.all()
    randomPlaylist = random.choice(playlists)
    plid = randomPlaylist.playlist_id
    # song_count = len(tracks)
    year = plid[:4]
    decade = plid[:3] + "0"
    print(plid)
    return JsonResponse((plid, decade, year), safe=False)


def chart_detail(request):
    if request.method == "GET":
        playlist_id = request.GET["chart_id"]
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
            tracks = playlist.track.all()
        except Exception:
            data["error_message"] = "error"
            return JsonResponse(data)
        data = list(tracks.values("track_id", "name", "artist", "spot_id", "img_url"))
        return JsonResponse(data, safe=False)


def add_playlist_to_app(request):
    spot_ids = []
    if request.method == "GET":
        charts = json.loads(request.GET["chart_data"])
        for chart in charts:
            spot_ids.append(chart["spot_id"])
        pl_name = request.GET["pl_name"]
        sp, user_id = login()
        pl_id = create_blank_plist(sp, user_id=user_id, pl_name=pl_name)
        populate_playlist(sp, user_id, pl_id, spot_ids)
    return render(request, "add_playlist_to_app.html", {})


def populate_playlist(sp, user_id, pl_id, track_ids):
    sp.user_playlist_add_tracks(user_id, pl_id, track_ids)


def create_blank_plist(sp, user_id, pl_name):
    sp.user_playlist_create(user_id, pl_name)
    playlists = sp.user_playlists(user_id)
    pl_id = ""
    for pl in playlists["items"]:
        if pl["name"] == pl_name:
            pl_id = pl["id"]
    return pl_id


def show_weeks(request):
    if request.method == "GET":
        year = request.GET["year"]
        try:
            playlists = Playlist.objects.filter(playlist_id__startswith=year)

        except Exception:
            print("Error occured")
            # data["error_message"] = "error"
            # return JsonResponse(data)
        return JsonResponse(list(playlists.values("playlist_id", "name")), safe=False)


def home(request):
    return render(request, "home.html", {})
