from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from spotipy import Spotify
from dotenv import load_dotenv
import os

load_dotenv()

CID = os.getenv("CID")
SECRET = os.getenv("SECRET")
SCOPE = "playlist-modify-public"
REDIRECT_URI = "http://localhost:8888/callback"


def login():
    sp_oauth = create_spotify_oauth()
    code = sp_oauth.get_auth_response(open_browser=True)
    token = sp_oauth.get_access_token(code, check_cache=False)
    sp = Spotify(auth=token["access_token"], requests_timeout=25)
    user_id = sp.current_user()["id"]
    print("sp: {}, username: {} ".format(sp.me(), user_id))
    return sp, user_id


def app_login():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CID, client_secret=SECRET
    )
    sp = Spotify(
        client_credentials_manager=client_credentials_manager, requests_timeout=25
    )
    return sp


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CID,
        client_secret=SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
    )
