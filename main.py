from datetime import date, timedelta, datetime
from ast import literal_eval
from bs4 import BeautifulSoup as BS
import os, requests, re, django, pickle, sys

sys.path.append("/path/to/chartz_project")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chartz_project.settings")
django.setup()
from chartify.login import app_login
from chartify.models import Playlist, Track


def main():
    _path = "C:\\Users\\jredd\\PycharmProjects\\mongo\\charts\\pkl_dest_test"

    # fdate = ["20230402", "20230409", "20230416", "20230430"]

    fdate = "20230521"
    # fn = fdate

    #### PRODUCTION CODE STARTS HERE ####

    # fdate = get_date_today()
    current_chart_url = create_url_from_date(fdate)
    chart = scrape_weekly_chart(fdate, current_chart_url)
    chart, do_not_exist = get_track_ids_from_spotify(chart)
    add_pl_and_tracks_to_db(chart, fdate)
    # pickle_dump(chart, _path, "cjart_w_ids")
    # write_to_txt_file(chart, _path, "cjart_w_ids")

    # chart, fdate = pickle_load(path, fdate)
    # pickle_dump(chart, path, fdate)
    # write_to_txt_file(chart, tpath, fdate)
    # add_chart_to_mongo(chart, collection=fdate)
    # data.sort(key=lambda a: a[2])


def pickled_charts_to_db(pickle_path):
    for file in os.listdir(pickle_path):
        fn, ext = os.path.splitext(file)
        chart, fn = pickle_load(pickle_path, fn)
        add_pl_and_tracks_to_db(chart, fn)


def add_pl_and_tracks_to_db(chart, fn):
    added, not_added = [], []
    plname = datetime.strptime(fn, "%Y%m%d").strftime("%Y - Week %U - %b %d")
    # create playlist in db, name format 19600104
    if not Playlist.objects.filter(playlist_id=fn).exists():
        playlist = Playlist.objects.create(playlist_id=fn, name=plname)
        print(playlist)
    else:
        pass
    for entry in chart:
        try:
            track_id, name, artist, img_url, spot_id = (
                entry[0],
                entry[1],
                entry[2],
                entry[4],
                entry[3],
            )
            track = Track.objects.create(
                track_id=track_id,
                name=name,
                artist=artist,
                spot_id=spot_id,
                img_url=img_url,
            )
            playlist.track.add(track)
            added.append(track)
        except:
            not_added.append(entry)
            # print("Song not added to playlist: {} - {}".format(name, artist))

    print("songs added: ", len(added))
    [print(song) for song in not_added]
    return added, not_added


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


def get_track_ids_from_spotify(chart):
    tracks_w_ids, do_not_exist = [], []
    sp = app_login()
    for entry in chart:
        title, artist = entry[1], entry[2]
        search_query = f"{title} {artist}"
        result = sp.search(q=search_query, limit=5, type="track")
        if result["tracks"]["total"] == 0:
            do_not_exist.append(entry)
            continue
        else:
            spot_id = result["tracks"]["items"][0]["id"]
            # print(spot_id)
            song_w_id = (*entry, spot_id)
            print(song_w_id)
            tracks_w_ids.append(song_w_id)
    return tracks_w_ids, do_not_exist


def scrape_weekly_chart(fdate, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
    res = requests.get(url, headers=headers)
    soup = BS(res.content, "html.parser")

    titles = [title.text.strip() for title in soup.find_all("div", class_="title")]
    artists = [artist.text.strip() for artist in soup.find_all("div", class_="artist")]
    img_urls = [img["src"] for img in soup.select(".chart img")]
    imgs = [img_url.replace("/img/60x60.gif", "/img/album.png") for img_url in img_urls]
    ranks = [i for i in range(1, len(titles) + 1)]

    track_ids = convert_rank_to_track_id(fdate, ranks)
    chart = [(track_ids[i], titles[i], artists[i], imgs[i]) for i in range(len(titles))]
    res.close()
    return chart


def convert_rank_to_track_id(fdate, ranks):
    track_ids = []
    for rank in ranks:
        if rank < 10:
            rank = "".join(["00", str(rank)])
        elif rank < 100:
            rank = "".join(["0", str(rank)])
        track_id = "".join([fdate, str(rank)])
        track_ids.append(track_id)
    return track_ids


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
        # print("Unpickling / opening data: ", complete_path)
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
    # main()
    _path = "C:\\Users\\jredd\\PycharmProjects\\mongo\\charts\\pkl_dest"
    pickled_charts_to_db(_path)
