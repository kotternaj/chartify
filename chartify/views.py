from django.http import JsonResponse
from django.shortcuts import render
import random, json
from .login import login
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
dbname = client["charts"]


def random_chart(request):
    all_collections = dbname.list_collection_names()
    randchart = random.choice(all_collections)
    year = randchart[:4]
    decade = randchart[:3] + "0"
    return JsonResponse((randchart, decade, year), safe=False)


def show_weeks(request):
    if request.method == "GET":
        year = request.GET["year"]
        charts = dbname.list_collection_names()
        # charts.sort(reverse=False)
        filter_by_yr = [chart for chart in charts if chart[:4] == year]
        filter_by_yr.sort(reverse=False)
        print(filter_by_yr[0:3])
        return JsonResponse(filter_by_yr, safe=False)


def chart_detail(request):
    if request.method == "GET":
        col = request.GET["chart_id"]
        print("Chart ID from chart_detail(): ", col)
        col = dbname[col]
        all_docs_in_col = [doc for doc in col.find({})]
        return JsonResponse(all_docs_in_col, safe=False)


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


def view_collection(db, col):
    col = db[col]
    all_docs_in_col = [doc for doc in col.find({})]
    return all_docs_in_col


def home(request):
    return render(request, "home.html", {})
