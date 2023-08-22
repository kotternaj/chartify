from django.http import JsonResponse
from django.shortcuts import render, redirect
import random, os, webbrowser, spotipy
from .models import Playlist
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()
CID = os.getenv("CID")
SECRET = os.getenv("SECRET")
SCOPE = os.getenv("SCOPE")
# REDIRECT_URI = os.getenv("REDIRECT_URI")
REDIRECT_URI = "http://localhost:8000/callback"


def add_playlist_to_app(request):
    if request.method == "GET":
        spot_ids = request.GET.getlist("spot_ids[]")
        pl_name = request.GET["pl_name"]
    pl_id = create_blank_plist(sp, user_id, pl_name)
    populate_playlist(sp, user_id, pl_id, spot_ids)
    return redirect("index")


def save_recent_chart(request):
    if request.method == "GET":
        chart = request.GET["chart"]
    return JsonResponse(chart, safe=False)


def login(request):
    sp_oauth = create_spotify_oauth(request)
    url = sp_oauth.get_authorize_url()
    webbrowser.open(url)
    return redirect(url)


def callback(request):
    global sp, token_info, user_id, sp_oauth
    sp_oauth = create_spotify_oauth(request)
    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)
    token = token_info["access_token"]
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()["id"]
    return redirect("chart")


# def refresh():
#     global token_info, sp
#     if sp_oauth.is_token_expired(token_info):
#         token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
#         token = token_info["access_token"]
#         sp = spotipy.Spotify(auth=token)


def create_spotify_oauth(request):
    cache_handler = spotipy.DjangoSessionCacheHandler(request=request)
    return SpotifyOAuth(
        client_id=CID,
        client_secret=SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_handler=cache_handler,
    )


def app_login():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CID, client_secret=SECRET
    )
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager, requests_timeout=25
    )
    return sp


def random_chart(request):
    if request.method == "GET":
        plid = request.GET["plid"]
        playlists = Playlist.objects.all()
        randomPlaylist = random.choice(playlists)
        plid = randomPlaylist.playlist_id
        year = plid[:4]
        decade = plid[:3] + "0"
        return JsonResponse((plid, decade, year), safe=False)


def show_weeks(request):
    if request.method == "GET":
        year = request.GET["year"]
        try:
            playlists = Playlist.objects.filter(playlist_id__startswith=year)
        except Exception:
            print("Error occured in show_weeks view")
        return JsonResponse(list(playlists.values("playlist_id", "name")), safe=False)


def chart_detail(request):
    if request.method == "GET":
        playlist_id = request.GET["chart_id"]
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
            pl_name = playlist.name
            tracks = playlist.track.all()
        except Exception:
            print("Error occured in chart_detail view")
        data = (
            list(tracks.values("track_id", "name", "artist", "spot_id", "img_url")),
            pl_name,
        )
        return JsonResponse(data, safe=False)


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


def index(request):
    return render(request, "index.html", {})


def chart(request):
    return render(request, "chart.html", {})
