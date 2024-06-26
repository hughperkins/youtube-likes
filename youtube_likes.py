# Note, if you run this from crontab, you should put the following in front
# of the python command:
# PYTHONIOENCODING=utf-8
# eg
# PYTHONIOENCODING=utf-8 python youtube_likes.py
# (otherwise it won't handle non-latin characters ok)

import argparse
import datetime
import json
import math
import os
import time
from typing import Any, Dict

# import warnings
from os import path

from ruamel.yaml import YAML

from youtube_likes_lib import process_logs, email_send_lib, youtube_query_lib, string_lib


yaml = YAML()

# warnings.simplefilter("ignore", yaml.error.UnsafeLoaderWarning)


g_delta_views_threshold_pct_by_delta_hours = {
    8: 40,
    24: 20,
    48: 10,
}


def get_stats_for_channel(config: Dict[str, Any], api_key: str, channel_id: str, channel_abbrev: str) -> Dict[str, Any]:
    persisted = {}

    uploads_playlist_id, persisted["num_subscriptions"] = youtube_query_lib.get_uploads_playlist_id_and_subscribers(
        api_key=api_key, channel_id=channel_id
    )
    print('uploads_playlist_lid', uploads_playlist_id)

    play_list_items = youtube_query_lib.get_playlist_items(
        channel_id=channel_id, api_key=api_key, uploads_playlist_id=uploads_playlist_id)
    print('len(play_list_items)', len(play_list_items))
    video_titles_ids = []
    print("titles:")
    for item in play_list_items:
        title = item["snippet"]["title"]
        print('- ', title)
        video_id = item["contentDetails"]["videoId"]
        video_titles_ids.append({"title": title, "video_id": video_id})

    print("finished fetching video_titles_ids", len(video_titles_ids))
    print('len(video_titles_ids)', len(video_titles_ids))

    video_ids = [v["video_id"] for v in video_titles_ids]

    videos = youtube_query_lib.get_videos(
        api_key=api_key,
        video_ids=video_ids,
    )

    print('')
    print('Get stats for each video:')
    video_infos = []
    persisted["videos"] = video_infos
    total_views = 0
    total_likes = 0
    for video in videos:
        if "short" in video["snippet"].get("tags", []):
            print(f"- [skip short \"{video['snippet']['title']}\"]")
            continue
        video_id = video["id"]
        title = video["snippet"]["title"]
        s = video["statistics"]
        likes = int(s.get("likeCount", 0))
        views = int(s.get("viewCount", 0))
        total_views += views
        total_likes += likes
        print(f"- {title} views {views} total_views {total_views}")
        favorites = int(s.get("favoriteCount", 0))
        comments = int(s.get("commentCount", 0))
        video_infos.append(
            {
                "video_id": video_id,
                "title": title,
                "likes": likes,
                "views": views,
                "favorites": favorites,
                "comments": comments,
            }
        )
    persisted["total_views"] = total_views
    persisted["total_likes"] = total_likes
    for d_hours in [8, 24, 48]:
        _res = process_logs.get_delta_stats(
            hours_delta=d_hours,
            views_log_filepath_templ=config["views_log_filepath_templ"],
            abbrev=channel_abbrev,
        )
        print(_res)
        persisted[f"delta{d_hours}"] = _res
    print('total_views', total_views, 'total_likes', total_likes)
    return persisted


def ensure_parent_folder_exists(filepath: str) -> None:
    view_dir = path.dirname(filepath)
    if not path.exists(view_dir):
        os.makedirs(view_dir)


def write_viewlogs(channel_abbrev: str, persisted, config):
    view_logfile = path.expanduser(config['views_log_filepath_templ'].format(abbrev=channel_abbrev))
    ensure_parent_folder_exists(view_logfile)
    dt = datetime.datetime.now()
    dt_string = dt.strftime("%Y%m%d-%H%M")
    res = {
        "subs": persisted["num_subscriptions"],
        "views": persisted["total_views"],
        "likes": persisted["total_likes"],
        "dt": dt_string
    }
    with open(view_logfile, 'a') as f:
        f.write("- " + json.dumps(res) + "\n")

    video_by_id = {video["video_id"]: video for video in persisted["videos"]}
    channel_config_by_abbrev = {config["abbrev"]: config for config in config["channels"]}
    channel_config = channel_config_by_abbrev[channel_abbrev]
    if "log_videos" not in channel_config:
        return
    for video_id in channel_config["log_videos"]:
        view_logfile = path.expanduser(config['views_by_video_log_filepath_templ'].format(
            abbrev=channel_abbrev, video_id=video_id))
        ensure_parent_folder_exists(view_logfile)
        video = video_by_id[video_id]
        res = {
            "views": video["views"],
            "likes": video["likes"],
            "comments": video["comments"],
            "favorites": video["favorites"],
            "dt": dt_string
        }
        with open(view_logfile, 'a') as f:
            f.write("- " + json.dumps(res) + "\n")


def analyse_video(channel_abbrev: str, old_video: Dict[str, Any], new_video: Dict[str, Any]) -> Dict[str, Any]:
    body = ""
    priority_reasons_title = ""
    priority_reasons_desc = ""
    is_priority = False

    video_title = new_video["title"]

    for k in new_video.keys():
        if (
            k == "comments"
            and video_title == "2 Create Unity RL env WITHOUT mlagents!"
            and int(new_video[k]) <= 2
        ):
            continue

        if k not in ["likes", "comments", "views", "dislikes"]:
            continue
        _old_value = int(old_video.get(k, "0"))
        _new_value = int(new_video.get(k, "0"))
        _change = _new_value - _old_value
        _chg_str = string_lib.int_to_signed_str(_change)
        if old_video.get(k, "") != new_video[k]:
            body += f"  {k} {_chg_str} => {_new_value}\n"

            if (
                k in ["views", "likes", "comments"]
                and _new_value > _old_value
            ):
                _letter = {"views": "v", "comments": "c", "likes": "l"}[k]
                if (_new_value // 100 != _old_value // 100) and channel_abbrev not in ['RL']:
                    priority_reasons_title += f" %100{_letter}"
                    priority_reasons_desc += (
                        f'- "{video_title}" %100{_letter}: {_new_value};\n'
                    )
                    is_priority = True
                elif (_new_value // 1000 != _old_value // 1000):
                    priority_reasons_title += f" %1000{_letter}"
                    priority_reasons_desc += (
                        f'- "{video_title}" %1000{_letter}: {_new_value};\n'
                    )
                    is_priority = True
                elif _change >= 20 and channel_abbrev not in ['RL']:
                    is_priority = True
                    priority_reasons_title += f" 20{_letter}"
                    priority_reasons_desc += f'- "{video_title}" 20{_letter} {_chg_str} => {_new_value};\n'
                elif _change > _old_value // 10:
                    is_priority = True
                    priority_reasons_title += f" 10p{_letter}"
                    priority_reasons_desc += f'- "{video_title}" 10p{_letter} {_chg_str} => {_new_value};\n'
                # total views passed a multiple of 100
    return {
        "body": body,
        "priority_reasons_desc": priority_reasons_desc,
        "priority_reasons_title": priority_reasons_title,
        "is_priority": is_priority,
    }


def process_channel(channel_id: str, channel_abbrev: str, api_key: str, config: Dict[str, Any]):
    channels = config["channels"]
    channel_name_by_id = {info["id"]: info["name"] for info in channels}
    channel_name = channel_name_by_id[channel_id]

    print('')
    print('============================================================')
    print(channel_abbrev)
    print(channel_name)
    print('')
    persisted = get_stats_for_channel(
        config=config, api_key=api_key, channel_id=channel_id, channel_abbrev=channel_abbrev)

    write_viewlogs(channel_abbrev=channel_abbrev, persisted=persisted, config=config)

    cache_file_path_templ = config["cache_file_path_templ"]
    cache_file_path = path.expanduser(cache_file_path_templ.format(abbrev=channel_abbrev))
    if path.isfile(cache_file_path):
        with open(cache_file_path, "r") as f:
            old_persisted = yaml.load(f)
    else:
        old_persisted = {"videos": [], "num_subscriptions": 0}

    is_priority = False

    priority_reasons_title = ""
    priority_reasons_desc = ""
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
            analysis = analyse_video(channel_abbrev=channel_abbrev, new_video=video, old_video=old_video)
            _body = analysis["body"]
            if _body.strip() != "":
                output_str += video["title"] + ":\n"
                print(f'_body [{_body}]')
                output_str += _body[:-1] + "\n"
            priority_reasons_title += analysis["priority_reasons_title"]
            priority_reasons_desc += analysis["priority_reasons_desc"]
            is_priority = is_priority or analysis["is_priority"]

    if persisted["num_subscriptions"] != old_persisted["num_subscriptions"]:
        is_priority = True
        priority_reasons_title += " sub"
        priority_reasons_desc += f'- Subs {old_persisted["num_subscriptions"]} => {persisted["num_subscriptions"]}\n'
        output_str += (
            "num subscriptions: %s => %s"
            % (old_persisted["num_subscriptions"], persisted["num_subscriptions"])
            + "\n"
        )

    if channel_abbrev in ['RL']:
        for d_hours in [8, 24, 48]:
            print(f'checking changes h_hours {d_hours}')
            _delta_key = f"delta{d_hours}"
            print(f'_delta_key {_delta_key}')
            if _delta_key in old_persisted and _delta_key in persisted:
                print(f'{_delta_key} in both old and new')
                old_d_views = old_persisted[_delta_key]["d_views"]
                new_d_views = persisted[_delta_key]["d_views"]
                d_views_diff = new_d_views - old_d_views
                print(f'd_views_diff {d_views_diff:.0f}')
                d_views_diff_pct = 0
                if new_d_views > 0:
                    d_views_diff_pct = d_views_diff / new_d_views * 100
                print(f'd_views_diff_pct {d_views_diff_pct:.0f}')
                if abs(d_views_diff_pct) > g_delta_views_threshold_pct_by_delta_hours[d_hours]:
                    print('is_priority')
                    is_priority = True
                    priority_reasons_title += f" DV{d_hours}"
                    priority_reasons_desc += f"- Delta views pct {d_hours}h {g_delta_views_threshold_pct_by_delta_hours[d_hours]}%: {old_d_views:.0f} => {new_d_views:.0f}\n"
                if abs(d_views_diff_pct) > 0:
                    output_str += f"- Delta views pct {d_hours}h: {old_d_views:.0f} => {new_d_views:.0f}\n"

    if path.exists(cache_file_path):
        mins_since_last_write = (time.time() - path.getmtime(cache_file_path)) / 60
    else:
        mins_since_last_write = math.inf

    print(f'output_str [{output_str}]')

    email_message = ""
    if output_str != "":
        email_message += channel_name + "\n"
        email_message += "=" * len(channel_name) + "\n"
        email_message += "\n"
        if is_priority:
            email_message += "Priority changes:\n"
            email_message += priority_reasons_desc
            email_message += "\n"
        email_message += "Details:\n"
        email_message += output_str
        # email_message += "\n"
    if priority_reasons_title != "":
        priority_reasons_title = priority_reasons_title.strip()
        priority_reasons_title = f" {channel_abbrev}[{priority_reasons_title}]"

    return {
        "channel_name": channel_name,
        "channel_abbrev": channel_abbrev,
        "is_priority": is_priority,
        "priority_reasons_title": priority_reasons_title,
        "priority_reasons_desc": priority_reasons_desc,
        # "body": output_str,
        "body": email_message,
        "persisted": persisted,
        "cache_file_path": cache_file_path,
        "mins_since_last_write": mins_since_last_write,
    }


def run(args):
    with open(args.config_file, "r") as f:
        config = yaml.load(f)

    api_key = config["api_key"]
    channels = config["channels"]
    channel_id_by_name = {info["name"]: info["id"] for info in channels}
    channel_abbrev_by_id = {info["id"]: info["abbrev"] for info in channels}

    results = []

    for _, channel_id in channel_id_by_name.items():
        channel_abbrev = channel_abbrev_by_id[channel_id]

        if args.abbrev is not None:
            if channel_abbrev.lower() != args.abbrev.lower():
                continue

        res = process_channel(channel_id=channel_id, channel_abbrev=channel_abbrev, api_key=api_key, config=config)
        results.append(res)

    global_email_message = ""
    global_priority_reasons_title = ""
    global_email_message_l = []
    for res in results:
        _body = res["body"]
        if res["body"] != "":
            _priority_reasons_title = res["priority_reasons_title"]
            global_email_message_l.append(_body)
            if _priority_reasons_title != "":
                _priority_reasons_title = _priority_reasons_title.strip()
                global_priority_reasons_title += f" {channel_abbrev}[{_priority_reasons_title}]"
    global_email_message = "\n".join(global_email_message_l)

    if global_email_message == "":
        print("No changes detected")
        return

    global_is_priority = any([res["is_priority"] for res in results])
    if args.priority:
        global_is_priority = True
    print("global_priority", global_is_priority)

    global_priority_reasons_title = " ".join([res["priority_reasons_title"] for res in results])
    print('')
    print("Subject: ", global_priority_reasons_title)
    print('')
    print(global_email_message)
    print('(end of email)')

    global_mins_since_last_write = max([res["mins_since_last_write"] for res in results])
    print(f'global_mins_since_last_write {global_mins_since_last_write:.1f}')
    if (
        not global_is_priority
        and global_mins_since_last_write < config["min_change_interval_minutes"]
    ):
        print(
            "skipping, since only %.1f" % global_mins_since_last_write, "mins since last write"
        )
        return

    if config["send_smtp"] and not args.no_send_email:
        subject = config["smtp_subject"]
        if global_is_priority:
            subject += global_priority_reasons_title
        email_send_lib.send_email(
            config["smtp_server"],
            config["smtp_port"],
            config["smtp_username"],
            config["smtp_password"],
            config["smtp_from_email"],
            config["smtp_to_email"],
            subject,
            global_email_message,
        )

    if not args.no_update_cache:
        for res in results:
            filepath = res["cache_file_path"]
            cache_dir = path.dirname(filepath)
            if not path.exists(cache_dir):
                os.makedirs(cache_dir)
            with open(filepath, "w") as f:
                yaml.dump(res["persisted"], f)
                print(f' wrote {filepath}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--no-send-email", action="store_true")
    parser.add_argument("--no-update-cache", action="store_true")
    parser.add_argument("--abbrev", help="process only this abbrev")
    parser.add_argument("--priority", action="store_true")
    args = parser.parse_args()
    run(args)
