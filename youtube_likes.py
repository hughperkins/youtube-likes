# Note, if you run this from crontab, you should put the following in front
# of the python command:
# PYTHONIOENCODING=utf-8
# eg
# PYTHONIOENCODING=utf-8 python youtube_likes.py
# (otherwise it won't handle non-latin characters ok)

import argparse
import email.message
import json
import smtplib
import time
import warnings
from email.mime.text import MIMEText
from os import path

import requests
from ruamel import yaml

warnings.simplefilter("ignore", yaml.error.UnsafeLoaderWarning)


def send_email(
    smtp_server,
    smtp_port,
    username,
    password,
    from_email,
    to_email,
    subject,
    message,
):
    # msg = email.message.EmailMessage()
    msg = MIMEText(
        "<html><body>"
        + message.replace(" ", "&nbsp;").replace("\n", "<br />")
        + "</body></html>",
        "html",
    )
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    # msg.set_content(message)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.login(username, password)
        smtp.sendmail(from_email, to_email, msg.as_string())


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
    # print(json.dumps(d, indent=2))
    persisted["num_subscriptions"] = d["items"][0]["statistics"]["subscriberCount"]
    # print('num_subscriptions %s')

    next_page_token = None
    videos = []
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
        for item in d["items"]:
            title = item["snippet"]["title"]
            # print(title)
            video_id = item["contentDetails"]["upload"]["videoId"]
            videos.append({"title": title, "video_id": video_id})
        # print(d.keys())
        print(d["pageInfo"])
        if "nextPageToken" in d:
            next_page_token = d["nextPageToken"]
            print("next_page_token", next_page_token)
        else:
            break
    print("finished fetching videos", len(videos))

    res = requests.get(
        "https://www.googleapis.com/youtube/v3/videos/?id={video_ids}"
        "&part=snippet%2CcontentDetails%2Cstatistics"
        "&key={api_key}".format(
            video_ids=",".join([v["video_id"] for v in videos]), api_key=api_key
        )
    )
    assert res.status_code == 200
    d = json.loads(res.content.decode("utf-8"))
    videos = []
    persisted["videos"] = videos
    for item in d["items"]:
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


def run(args):
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)
    # print('config', config)

    email_message = ""

    api_key = config["api_key"]
    channels = config["channels"]
    channel_id_by_name = {info["name"]: info["id"] for info in channels}
    channel_name_by_id = {info["id"]: info["name"] for info in channels}

    persisted_all_channels = {}

    for channel_name, channel_id in channel_id_by_name.items():
        persisted = get_persisted_for_channel(api_key=api_key, channel_id=channel_id)
        persisted_all_channels[channel_id] = persisted
    # print(yaml.dump(videos))
    # print(json.dumps(videos, indent=2))
    # print(json.dumps(videos, indent=2))
    if path.isfile(config["cache_file"]):
        with open(config["cache_file"], "r") as f:
            old_persisted_all_channels = yaml.load(f)
    else:
        # old_stats = []
        old_persisted_all_channels = {}
        # old_persisted = {'videos': [], 'num_subscriptions': 0}

    is_priority = False

    for channel_name, channel_id in channel_id_by_name.items():
        # print(channel_name, channel_id)
        # print(old_persisted_all_channels[channel_id])
        persisted = persisted_all_channels[channel_id]
        old_persisted = old_persisted_all_channels.get(
            channel_id, {"videos": [], "num_subscriptions": 0}
        )
        output_str = ""
        videos = persisted["videos"]
        old_videos = old_persisted["videos"]
        old_by_id = {}
        for video in old_videos:
            old_by_id[video["video_id"]] = video
        new_by_id = {}
        for video in videos:
            new_by_id[video["video_id"]] = video
        for video_id, video in new_by_id.items():
            if video_id not in old_by_id:
                output_str += "new:\n"
                output_str += json.dumps(video, indent=2) + "\n"
            else:
                old_video = old_by_id[video_id]
                # if json.dumps(old_video) != json.dumps(video):
                # print(json.dumps(sorted(old_video.items())))
                # print(json.dumps(sorted(video.items())))
                output = ""
                for k in video.keys():
                    # if k == 'video_id':
                    #     continue
                    if old_video[k] != video[k]:
                        output += "  %s %s => %s\n" % (k, old_video[k], video[k])
                        if k in ["likes", "comments"]:
                            is_priority = True
                        if k == "views":
                            _old_views = int(old_video.get(k, "0"))
                            _new_views = int(video[k])
                            _view_change = _new_views - _old_views
                            if _old_views == 0:
                                is_priority = True
                            if _view_change > _old_views // 10:
                                is_priority = True
                            if _view_change >= 20:
                                is_priority = True
                            # total views passed a multiple of 100
                            if _new_views // 100 != _old_views // 100:
                                is_priority = True
                if output != "":
                    output_str += video["title"] + ":\n"
                    output_str += output[:-1] + "\n"

        if persisted["num_subscriptions"] != old_persisted["num_subscriptions"]:
            # _old_subs = int(old_persisted.get('num_subscriptions', 0))
            # new_subs += int(persisted['num_subscriptions']) - _old_subs
            is_priority = True
            output_str += (
                "num subscriptions: %s => %s"
                % (old_persisted["num_subscriptions"], persisted["num_subscriptions"])
                + "\n"
            )
        if output_str != "":
            print(channel_name)
            print(output_str)
            print()
            email_message += channel_name + "\n"
            email_message += output_str + "\n"
            email_message += "\n"

    if email_message == "":
        print("No changes detected")
        return

    print("is_priority", is_priority)

    # is_priority = False
    # if 'likes'
    # if (
    #     'geometry dash' in email_message.lower() or
    #     'trigonometric mash' in email_message.lower()
    # ):
    #     is_priority = True

    mins_since_last_write = (time.time() - path.getmtime(config["cache_file"])) / 60
    if (
        not is_priority
        and mins_since_last_write < config["min_change_interval_minutes"]
    ):
        print(
            "skipping, since only %.1f" % mins_since_last_write, "mins since last write"
        )
        return

    if config["send_smtp"] and not args.no_send:
        subject = config["smtp_subject"]
        if has_gd:
            subject += " has gd!"
        send_email(
            config["smtp_server"],
            config["smtp_port"],
            config["smtp_username"],
            config["smtp_password"],
            config["smtp_from_email"],
            config["smtp_to_email"],
            subject,
            email_message,
        )

    with open(config["cache_file"], "w") as f:
        yaml.dump(persisted_all_channels, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--no-send", action="store_true")
    args = parser.parse_args()
    run(args)
