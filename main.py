from datetime import date, timedelta, datetime
from ast import literal_eval
from bs4 import BeautifulSoup as BS
import os, requests, re, django, pickle, sys
from ast import literal_eval


sys.path.append("/path/to/chartz_project")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chartz_project.settings")
django.setup()
from chartify.login import app_login
from chartify.models import Playlist, Track


def main2():
    fdate = get_date_today()
    current_chart_url = create_url_from_date(fdate)
    chart = scrape_weekly_chart(fdate, current_chart_url)
    chart = get_track_ids_from_spotify(chart)
    add_pl_and_tracks_to_db(chart, fdate)


def main():
    # update_img_urls()
    # find_pl_in_db()
    # add_s_to_http_img_urls()
    # count_http()
    get_all_img_urls()


def find_pl_in_db():
    plid = "19820905"
    pl = Playlist.objects.get(pk=plid)
    tracks = pl.track.all()
    # for t in tracks:
    #     print(t.name)
    #     print(t.img_url)
    return tracks


def count_http():
    tracks = Track.objects.all()
    http = [t for t in tracks if t.img_url[0:5] == "http:"]
    https = [t for t in tracks if t.img_url[0:6] == "https:"]
    default = [t for t in tracks if t.img_url == "/img/album.png"]
    print(f"{len(http)}  - {len(https)}  -  {len(default)}")


def get_all_img_urls():
    album_art_dir = "C:\\Users\\jredd\\Desktop\\code\\chartz\\album_art"
    tracks = Track.objects.all()
    all_img_urls = [(t.track_id, t.img_url) for t in tracks]
    write_to_txt_file(all_img_urls, album_art_dir, "all_img_urls")
    print(all_img_urls[0:3])
    print(len(all_img_urls))


def download_imgs(urls):
    # urls = ["http://localhost:8000/img/album.png"]
    album_art_dir = "C:\\Users\\jredd\\Desktop\\code\\chartz\\album_art"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }

    for url in urls:
        # res = requests.get(url, stream=True)
        res = requests.get(url, headers=headers, stream=True)
        res.raw.decode_content = True
        with open(album_art_dir, "wb") as f:
            f.write(res.content)


def add_s_to_http_img_urls():
    # tracks = find_pl_in_db()
    # print(len(tracks))
    count = 0
    tracks = Track.objects.all()
    # [print(t.img_url) for t in tracks]
    for track in tracks:
        if track.img_url[0:5] == "http:":
            # print(track)
            track.img_url = track.img_url.replace(":", "s:")
            # track.img_url.replace(":", "s:")
            track.save()
            count += 1
    print(count)
    # [
    #     track.save(track.img_url.replace(":", "s:"))
    #     for track in tracks
    #     if track.img_url[0:5] == "http:"
    # ]


def update_img_urls():
    # all_charts = []
    replace_urls = [
        "/fallback/artwork-cobalt.svg",
        "https://m.media-amazon.com/images/I/01RmK+J4pJL._SL500_.gif",
        "/fallback/artwork-pink.svg",
    ]
    count = 0
    tracks = Track.objects.all()
    for track in tracks:
        if track.img_url in replace_urls:
            # if track.img_url[0:38] == "https://d35iaml2i6ojwd.cloudfront.net/":
            track.img_url = "/img/album.png"
            track.save()
            print(track.track_id)
            print(track.name)
            print(track.img_url)
            count += 1
    print(count)

    # tpath = "C:\\Users\\jredd\\PycharmProjects\\spotifyapp\\charts\\new_charts\\emptys"
    # chart = read_txt_file(tpath, "redo.txt")
    # chart = make_tuple(chart)
    # for track in tracks:
    #     for c in chart:
    #         print(chart)
    #         if track.track_id == c[0]:
    #             track.img_url = "/img/album.png"
    #             track.save()

    # for txt_file in os.listdir(tpath):
    #     data = read_txt_file(tpath, txt_file)
    #     chart = make_tuple(data)
    #     print(chart[0])
    #     all_charts.append(chart)
    #     for track in tracks:
    #         for c in chart:
    #             if track.track_id == c[0]:
    #                 track.img_url = c[3]
    #                 track.save()


def read_txt_file(path, filename):
    # if filename[:-4] != ".txt":
    #     filename = filename + ".txt"
    complete_path = os.path.join(path, filename)
    with open(complete_path, "r") as f:
        data = [line.strip() for line in f]
    return data


def write_to_txt_file(data, path, filename):
    complete_path = os.path.join(path, filename + ".txt")
    with open(complete_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(str(item))
            f.write("\n")
    print("text file created: ", filename)


def make_tuple(data):
    data = [literal_eval(x) for x in data]
    return data


def add_pl_and_tracks_to_db(chart, fn):
    added = []
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
                entry[3],
                entry[4],
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
            continue
    return added


def get_track_ids_from_spotify(chart):
    tracks_w_ids = []
    sp = app_login()
    for entry in chart:
        title, artist = entry[1], entry[2]
        search_query = f"{title} {artist}"
        result = sp.search(q=search_query, limit=5, type="track")
        if result["tracks"]["total"] == 0:
            continue
        else:
            spot_id = result["tracks"]["items"][0]["id"]
            song_w_id = (*entry, spot_id)
            tracks_w_ids.append(song_w_id)
    return tracks_w_ids


def scrape_weekly_chart(fdate, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
    res = requests.get(url, headers=headers)
    soup = BS(res.content, "html.parser")

    titles = [
        title.contents[-1].text.strip()
        for title in soup.find_all("a", class_="chart-name")
    ]
    # print(titles)
    # print(len(titles))
    artists = [
        artist.text.strip() for artist in soup.find_all("a", class_="chart-artist")
    ]
    # print(len(artists))
    img_urls = [img["src"] for img in soup.find_all("img", class_="chart-image-large")]
    # print(len(img_urls))
    imgs = [img_url.replace("/img/60x60.gif", "/img/album.png") for img_url in img_urls]
    ranks = [i for i in range(1, len(titles) + 1)]

    track_ids = convert_rank_to_track_id(fdate, ranks)
    chart = [(track_ids[i], titles[i], artists[i], imgs[i]) for i in range(len(titles))]
    res.close()
    return chart


# def scrape_weekly_chart(fdate, url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
#     }
#     res = requests.get(url, headers=headers)
#     soup = BS(res.content, "html.parser")

#     titles = [title.text.strip() for title in soup.find_all("div", class_="title")]
#     artists = [artist.text.strip() for artist in soup.find_all("div", class_="artist")]
#     img_urls = [img["src"] for img in soup.select(".chart img")]
#     imgs = [img_url.replace("/img/60x60.gif", "/img/album.png") for img_url in img_urls]
#     ranks = [i for i in range(1, len(titles) + 1)]

#     track_ids = convert_rank_to_track_id(fdate, ranks)
#     chart = [(track_ids[i], titles[i], artists[i], imgs[i]) for i in range(len(titles))]
#     res.close()
#     return chart


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
