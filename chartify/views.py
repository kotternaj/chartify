from django.http import JsonResponse
from django.shortcuts import render, redirect
import random
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from .login import login
from .models import Playlist
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
from django.http import HttpResponseRedirect, HttpResponse
import os
import webbrowser

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


# works
def login(request):
    sp_oauth = create_spotify_oauth(request)
    url = sp_oauth.get_authorize_url()
    webbrowser.open(url)
    return redirect(url)


# works
def callback(request):
    global sp, token_info, user_id, sp_oauth
    print("CALLBACK")
    sp_oauth = create_spotify_oauth(request)
    # token_info = sp_oauth.get_cached_token()
    # if not token_info:
    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)
    token = token_info["access_token"]
    # request.session["access_token"] = access_token
    sp = spotipy.Spotify(auth=token)
    # sp = spotipy.Spotify(
    #     auth=token_info["access_token"], requests_timeout=25, requests_session=True
    # )
    user_id = sp.current_user()["id"]
    # else:
    #     refresh()
    return redirect("index")
    # return render(request, "home.html", {})


# def refresh():
#     global token_info, sp
#     if sp_oauth.is_token_expired(token_info):
#         token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
#         token = token_info["access_token"]
#         sp = spotipy.Spotify(auth=token)


def create_spotify_oauth(request):
    # print("request sent to create_oauth func: ", request)
    cache_handler = spotipy.DjangoSessionCacheHandler(request=request)
    return SpotifyOAuth(
        client_id=CID,
        client_secret=SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_handler=cache_handler,
    )


# ORIGINAL
def loginO(request):
    sp_oauth = create_spotify_oauth(request)
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    # code = sp_oauth.get_auth_response(open_browser=True)
    # token = sp_oauth.get_access_token(code, check_cache=False)
    # sp = spotipy.Spotify(auth=token["access_token"], requests_timeout=25)

    user_id = sp.current_user()["id"]
    print("sp: {}, username: {} ".format(sp.me(), user_id))
    return sp, user_id


def app_login():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CID, client_secret=SECRET
    )
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager, requests_timeout=25
    )
    return sp


def random_chart(request):
    playlists = Playlist.objects.all()
    randomPlaylist = random.choice(playlists)
    plid = randomPlaylist.playlist_id
    year = plid[:4]
    decade = plid[:3] + "0"
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
        print(playlist_id)
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


def show_weeks(request):
    if request.method == "GET":
        year = request.GET["year"]
        try:
            playlists = Playlist.objects.filter(playlist_id__startswith=year)
        except Exception:
            print("Error occured")
        return JsonResponse(list(playlists.values("playlist_id", "name")), safe=False)


# def home(request):
#     return render(request, "home.html", {})


def index(request):
    return render(request, "index.html", {})


def splash(request):
    return render(request, "splash.html", {})
