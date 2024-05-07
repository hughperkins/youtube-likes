import argparse
import json
import requests
from ruamel.yaml import YAML


yaml = YAML()


def get_persisted_for_channel(api_key, channel_id):
    persisted = {}
    res = requests.get(
        "https://www.googleapis.com/youtube/v3/channels/?id={channel_id}"
        "&part=statistics"
        "&key={api_key}".format(channel_id=channel_id, api_key=api_key)
    )
    if res.status_code != 200:
        print("res.status_code %s" % res.status_code)
        print(res.content)
        raise Exception("invalid status code %s" % res.status_code)
    d = json.loads(res.content.decode("utf-8"))
    print('statistics', json.dumps(d, indent=2))
    persisted["num_subscriptions"] = d["items"][0]["statistics"]["subscriberCount"]

    next_page_token = None
    video_titles_ids = []
    while True:
        next_page_token_str = (
            f"&pageToken={next_page_token}" if next_page_token is not None else ""
        )
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/activities/?maxResults=50"
            "&channelId={channel_id}"
            "&part=snippet%2CcontentDetails"
            "&key={api_key}".format(api_key=api_key, channel_id=channel_id)
            + next_page_token_str
        )
        if res.status_code != 200:
            print("res.status_code %s" % res.status_code)
            print(res.content)
        assert res.status_code == 200
        d = json.loads(res.content.decode("utf-8"))
        # print(d.keys())
        # print('activities', json.dumps(d, indent=2))
        for item in d["items"]:
            title = item["snippet"]["title"]
            if "upload" not in item["contentDetails"]:
                continue
            # print(json.dumps(item, indent=2))
            video_id = item["contentDetails"]["upload"]["videoId"]
            video_titles_ids.append({"title": title, "video_id": video_id})
        print(d["pageInfo"])
        if "nextPageToken" in d:
            next_page_token = d["nextPageToken"]
            print("next_page_token", next_page_token)
        else:
            break
    print("finished fetching video_titles_ids", len(video_titles_ids))

    page_size = 50
    num_pages = (len(video_titles_ids) + page_size - 1) // page_size
    print("num_pages", num_pages)
    videos = []
    persisted["videos"] = videos
    for page_idx in range(num_pages):
        video_batch = video_titles_ids[
            page_idx * page_size : (page_idx + 1) * page_size
        ]
        _url = (
            "https://www.googleapis.com/youtube/v3/videos/?id={video_ids}"
            "&part=snippet%2CcontentDetails%2Cstatistics"
            "&key={api_key}".format(
                video_ids=",".join([v["video_id"] for v in video_batch]),
                api_key=api_key,
            )
        )
        print(_url)
        res = requests.get(_url)
        if res.status_code >= 400:
            print(res.status_code)
            print(res.content.decode("utf-8"))
        assert res.status_code == 200
        d = json.loads(res.content.decode("utf-8"))
        for item in d["items"]:
            print(json.dumps(item, indent=2))
            video_id = item["id"]
            title = item["snippet"]["title"]
            s = item["statistics"]
            likes = s.get("likeCount", 0)
            views = s.get("viewCount", 0)
            favorites = s.get("favoriteCount", 0)
            comments = s.get("commentCount", 0)
            videos.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "likes": likes,
                    "views": views,
                    "favorites": favorites,
                    "comments": comments,
                }
            )
    return persisted


def int_to_signed_str(v: int) -> str:
    if v > 0:
        return f"+{v}"
    elif v == 0:
        return "0"
    else:
        return str(v)


def run(args):
    with open(args.config_file, "r") as f:
        config = yaml.load(f)

    api_key = config["api_key"]
    persisted = get_persisted_for_channel(api_key=api_key, channel_id=args.channel_id)
    print(persisted)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--channel-id", type=str, required=True)
    args = parser.parse_args()
    run(args)
