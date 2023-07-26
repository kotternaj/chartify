from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
from django.http import HttpResponseRedirect
import os
from requests import Request
import spotipy.util as util
from django.shortcuts import redirect
import webbrowser

load_dotenv()

CID = os.getenv("CID")
SECRET = os.getenv("SECRET")
SCOPE = "playlist-modify-public"
# REDIRECT_URI = "http://localhost:8000"
REDIRECT_URI = "http://localhost:8000/callback"


# ORIGINAL
def login():
    sp_oauth = create_spotify_oauth()
    # sp = spotipy.Spotify(auth_manager=sp_oauth)
    url = sp_oauth.get_authorize_url()
    webbrowser.open(url)
    return redirect(url)

    # code = sp_oauth.get_auth_response(open_browser=True)
    # token = sp_oauth.get_access_token(code, check_cache=False)
    # sp = spotipy.Spotify(auth=token["access_token"], requests_timeout=25)

    # user_id = sp.current_user()["id"]
    # print("sp: {}, username: {} ".format(sp.me(), user_id))
    # return sp, user_id


def create_spotify_oauth():
    # cache_handler = spotipy.DjangoSessionCacheHandler(request=request)
    return SpotifyOAuth(
        client_id=CID,
        client_secret=SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        # cache_handler=cache_handler,
    )


# ORIGINAL
# def login(request):
#     sp_oauth = create_spotify_oauth(request)
#     sp = spotipy.Spotify(auth_manager=sp_oauth)

#     # code = sp_oauth.get_auth_response(open_browser=True)
#     # token = sp_oauth.get_access_token(code, check_cache=False)
#     # sp = spotipy.Spotify(auth=token["access_token"], requests_timeout=25)

#     user_id = sp.current_user()["id"]
#     print("sp: {}, username: {} ".format(sp.me(), user_id))
#     return sp, user_id


# def create_spotify_oauth(request):
#     cache_handler = spotipy.DjangoSessionCacheHandler(request=request)
#     return SpotifyOAuth(
#         client_id=CID,
#         client_secret=SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE,
#         show_dialog=True,
#         cache_handler=cache_handler,
#     )


def app_login():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CID, client_secret=SECRET
    )
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager, requests_timeout=25
    )
    return sp


def login2(request):
    url = (
        Request(
            "GET",
            "https://accounts.spotify.com/authorize",
            params={
                "scope": SCOPE,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "client_id": CID,
            },
        )
        .prepare()
        .url
    )

    print(url)
    webbrowser.open(url)
    # return HttpResponseRedirect(url)


# def login():
#     # Create a SpotifyOAuth object
#     sp_oauth = create_spotify_oauth()

#     # Print the sp_oauth object to the console
#     print("\n\nSP_OAuth Object:", sp_oauth, "\n\n")

#     # Redirect the user to the Spotify login page
#     # Get the authorization URL
#     url = sp_oauth.get_authorize_url()
#     # Print the authorization url to the console
#     print(url)
#     return redirect(url)

#     # Redirect the user to the Spotify login page
#     # return HttpResponseRedirect(url)


def callback2(request):
    sp_oauth = create_spotify_oauth(request)

    # Get the authorization code from the query parameters
    code = request.GET.get("code")

    # Request an access token using the authorization code
    token_info = sp_oauth.get_access_token(code)

    # Extract the access token
    access_token = token_info["access_token"]

    # Store the access token in a secure way (e.g. in a session or database)
    request.session["access_token"] = access_token


def login2(request):
    sp_oauth = create_spotify_oauth(request)
    # auth url pops up right here
    print(sp_oauth)

    code = sp_oauth.get_auth_response()
    print(code)
    token = sp_oauth.get_access_token(code, check_cache=False)
    print(token)
    # token = util.prompt_for_user_token(code)
    sp = spotipy.Spotify(auth=token["access_token"], requests_timeout=25)
    user_id = sp.current_user()["id"]
    print("sp: {}, username: {} ".format(sp.me(), user_id))
    return sp, user_id


# def create_spotify_oauth():
#     # spotipy.cache_handler
#     # cache_handler = spotipy.DjangoSessionCacheHandler(request=request)
#     return SpotifyOAuth(
#         client_id=CID,
#         client_secret=SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE,
#         show_dialog=True,
#         # cache_handler=cache_handler,
#     )


# def login(request):
#     sp_oauth = create_spotify_oauth()
#     print("URL OPENS")
#     code = sp_oauth.get_auth_response(open_browser=True)
#     print("CODE: ", code)
#     token = sp_oauth.get_access_token(code, check_cache=False)
#     print("TOKEN: ", token)
# sp = spotipy.Spotify(auth=token["access_token"], requests_timeout=25)
# user_id = sp.current_user()["id"]
# return sp, user_id


# def create_spotify_oauth():
#     cache_handler = spotipy.cache_handler.CacheFileHandler()
#     return SpotifyOAuth(
#         client_id=CID,
#         client_secret=SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE,
#         show_dialog=True,
#         cache_handler=cache_handler,
#     )


# def login():
#     auth_manager = spotipy.oauth2.SpotifyOAuth(
#         client_id=CID,
#         client_secret=SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE,
#         show_dialog=True,
#     )

#     # Redirect the user back to root again after authentication.
#     if request.args.get("code"):
#         auth_manager.get_access_token(request.args.get("code"), as_dict=False)
#         return redirect("/")

#     # If no token is found, render the base.html with the authentication link.
#     if not auth_manager.validate_token(cache_handler.get_cached_token()):
#         auth_url = auth_manager.get_authorize_url()
#         return render_template("login.html", auth_url=auth_url)

#     # Get the access token value from the token dict in OAuth2 object.
#     access_token = auth_manager.get_access_token()["access_token"]

#     # If a token is found (logged in), render the content from index instead.
#     return render_template("base.html", access_token=access_token)


if __name__ == "__main__":
    res = login()
