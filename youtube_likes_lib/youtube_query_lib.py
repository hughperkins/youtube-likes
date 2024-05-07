from typing import Tuple, List
import json
import requests


def get_uploads_playlist_id_and_subscribers(api_key: str, channel_id: str) -> Tuple[str, int]:
    res = requests.get(
        "https://www.googleapis.com/youtube/v3/channels/?id={channel_id}"
        "&part=statistics,contentDetails"
        "&key={api_key}".format(channel_id=channel_id, api_key=api_key)
    )
    if res.status_code != 200:
        print("res.status_code %s" % res.status_code)
        print(res.content)
        raise Exception("invalid status code %s" % res.status_code)
    d = json.loads(res.content.decode("utf-8"))
    item = d['items'][0]
    uploads_playlist_id = item['contentDetails']['relatedPlaylists']['uploads']
    print('uploads_playlist_id', uploads_playlist_id)
    num_subscriptions = int(item["statistics"]["subscriberCount"])
    return uploads_playlist_id, num_subscriptions


def get_playlist_items(
    api_key: str,
    channel_id: str,
    uploads_playlist_id: str,      
):
    next_page_token = None
    items = []
    num_pages = 0
    while True:
        next_page_token_str = (
            f"&pageToken={next_page_token}" if next_page_token is not None else ""
        )
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems/?maxResults=50"
            f"&playlistId={uploads_playlist_id}"
            f"&channelId={channel_id}"
            "&part=snippet%2CcontentDetails"
            f"&key={api_key}"
            f"{next_page_token_str}"
        )
        if res.status_code != 200:
            print("res.status_code %s" % res.status_code)
            print(res.content)
        assert res.status_code == 200
        d = json.loads(res.content.decode("utf-8"))
        items += d["items"]
        num_pages += 1
        if "nextPageToken" in d:
            next_page_token = d["nextPageToken"]
        else:
            break
    return items


def get_videos(api_key: str, video_ids: List[str]):
    page_size = 50
    num_pages = (len(video_ids) + 50 - 1) // 50
    videos = []
    for page_idx in range(num_pages):
        video_batch = video_ids[
            page_idx * page_size : (page_idx + 1) * page_size
        ]
        _url = (
            "https://www.googleapis.com/youtube/v3/videos/?id={video_ids}"
            "&part=snippet%2CcontentDetails%2Cstatistics"
            "&key={api_key}".format(
                video_ids=",".join(video_batch),
                api_key=api_key,
            )
        )
        res = requests.get(_url)
        if res.status_code >= 400:
            print(res.status_code)
            print(res.content.decode("utf-8"))
        assert res.status_code == 200
        d = json.loads(res.content.decode("utf-8"))
        videos += d["items"]
    return videos
