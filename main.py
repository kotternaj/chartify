from datetime import date, timedelta, datetime
from ast import literal_eval
from bs4 import BeautifulSoup as BS
import os, requests, re, django, pickle, sys

sys.path.append("/path/to/chartz_project")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chartz_project.settings")
django.setup()
# from pages.models import Track, Playlist
from chartify.login import app_login
from pymongo import MongoClient


def main():
    # cwd = os.getcwd()
    # path = cwd + "\charts"
    # path = "C:\\Users\\jredd\\PycharmProjects\\spotifyapp\\charts"
    path = "C:\\projects\\spot\\all_pkl_new"
    tpath = "C:\\projects\\spot\\all_txt"
    # dne_path = "C:\\projects\\spot\\dne"
    fdates = ["20230507", "20230514", "20230521"]
    # fdate = "20230507"

    #### PRODUCTION CODE STARTS HERE ####

    # fdate = get_date_today()
    for fdate in fdates:
        current_chart_url = create_url_from_date(fdate)
        chart = scrape_weekly_chart(current_chart_url)
        chart, do_not_exist = get_track_ids_from_spotify(chart)
        add_chart_to_mongo(chart, collection=fdate)

    # chart, fdate = pickle_load(path, fdate)
    # pickle_dump(chart, path, fdate)
    # write_to_txt_file(chart, tpath, fdate)
    # add_pl_and_tracks_to_db(chart, fn)
    # data.sort(key=lambda a: a[2])


def add_chart_to_mongo(chart_data, collection):
    lst = []
    client = MongoClient("mongodb://localhost:27017/")
    dbname = client["charts"]
    # print(chart_data)
    for entry in chart_data:
        entry = {
            "_id": entry[2],
            "title": entry[0],
            "artist": entry[1],
            "spot_id": entry[4],
            "img_url": entry[3],
        }
        lst.append(entry)
    print(lst)
    col = dbname[collection]
    col.insert_many(lst)


# def add_pl_and_tracks_to_db(chart, fn):
#     added, not_added = [], []
#     plname = datetime.strptime(fn, "%Y%m%d").strftime("%Y - wk %U - %b %d")
#     # create playlist in db, name format 19600104
#     if not Playlist.objects.filter(playlist_id=fn).exists():
#         playlist, created = Playlist.objects.get_or_create(playlist_id=fn, name=plname)
#         print("Playlist {} added to DB".format(plname))
#     for entry in chart:
#         try:
#             song_name, artist, img_url, spot_id = entry[0], entry[1], entry[3], entry[4]
#             rank = entry[2]
#             track, created = Track.objects.get_or_create(
#                 name=song_name, artist=artist, img_url=img_url, spot_id=spot_id
#             )
#             playlist.track.add(track)
#             added.append(track)
#         except:
#             not_added.append(song_name)
#             print(
#                 "Song not added to playlist: {} - {}  {}".format(
#                     song_name, artist, rank
#                 )
#             )
#     print("songs added: ", len(added))
#     print("Songs not added: ", len(not_added))
#     return added, not_added


def create_blank_plist(sp, user_id, pl_name):
    sp.user_playlist_create(user_id, pl_name)
    playlists = sp.user_playlists(user_id)
    pl_id = ""
    for pl in playlists["items"]:
        if pl["name"] == pl_name:
            pl_id = pl["id"]
    return pl_id


def populate_playlist(sp, user_id, pl_id, track_ids):
    sp.user_playlist_add_tracks(user_id, pl_id, track_ids)


# def check_if_track_in_db(chart):
#     new_chart = []
#     for entry in chart:
#         print("{} {}".format(entry[0], entry[1]))
#         if not Track.objects.filter(name=entry[0]).filter(artist=entry[1]):
#             new_chart.append(entry)
#     print(new_chart)
#     return new_chart


def get_track_ids_from_spotify(chart):
    tracks_w_ids, do_not_exist = [], []
    sp = app_login()
    for entry in chart:
        title, artist = entry[0], entry[1]
        search_query = f"{title} {artist}"
        result = sp.search(q=search_query, limit=5, type="track")
        if result["tracks"]["total"] == 0:
            do_not_exist.append(entry)
            continue
        else:
            track_id = result["tracks"]["items"][0]["id"]
            print(track_id)
            song_w_id = (*entry, track_id)
            print(song_w_id)
            tracks_w_ids.append(song_w_id)
    return tracks_w_ids, do_not_exist


def scrape_weekly_chart(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
    res = requests.get(url, headers=headers)
    soup = BS(res.content, "html.parser")

    titles = [title.text.strip() for title in soup.find_all("div", class_="title")]
    artists = [artist.text.strip() for artist in soup.find_all("div", class_="artist")]
    imgs = [img["src"] for img in soup.select(".chart img")]
    ranks = [i for i in range(1, len(titles) + 1)]

    chart = [(titles[i], artists[i], ranks[i], imgs[i]) for i in range(len(titles))]
    res.close()
    return chart


def get_date_from_url(url):
    date_string = re.findall(r"\D(\d{8})\D", url)[0]
    return date_string


def pickle_dump(data, path, filename):
    complete_path = os.path.join(path, filename + ".pkl")
    with open(complete_path, "wb") as f:
        pickle.dump(data, f)
        print("Data pickled: ", complete_path)


def pickle_load(path, filename):
    fn = filename
    if filename[:-4] != ".pkl":
        filename = filename + ".pkl"
    complete_path = os.path.join(path, filename)
    # filename = os.path.basename(os.path.normpath(filename))

    with open(complete_path, "rb") as f:
        print("Unpickling / opening data: ", complete_path)
        udata = pickle.load(f)
    return udata, fn


def write_to_txt_file(data, path, filename):
    complete_path = os.path.join(path, filename + ".txt")
    with open(complete_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(str(item))
            f.write("\n")
    print("text file created: ", filename)


def append_to_txt_file(data, path, filename):
    complete_path = os.path.join(path, filename + ".txt")
    with open(complete_path, "a", encoding="utf-8") as f:
        for item in data:
            f.write(str(item))
            f.write("\n")
    print("text file appended: ", filename)


def read_txt_file(path, filename):
    if filename[:-4] != ".txt":
        filename = filename + ".txt"
    complete_path = os.path.join(path, filename)
    with open(complete_path, "r") as f:
        print("opening data: ", complete_path)
        data = [line.strip() for line in f]
        # data = [line for line in f]
    return data


def make_tuple(data):
    data = [literal_eval(x) for x in data]
    return data


def get_date_today():
    now = datetime.now()
    fdate = now.strftime("%Y%m%d")
    return fdate


def create_url_from_date(today):
    url_prefix = "https://www.officialcharts.com/charts/singles-chart/"
    url_suffix = "7501/"
    url = os.path.join(url_prefix, str(today), url_suffix).replace("\\", "/")
    return url


if __name__ == "__main__":
    main()
    # fdate = "20230409"
    # path = "C:\\projects\\spot\\charts"
    # udata, fn = pickle_load(path, fdate)
    # print(udata)
    # add_pl_and_tracks_to_db(udata, fn)
