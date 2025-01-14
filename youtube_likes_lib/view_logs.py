from dataclasses import dataclass
import datetime
import json
from os import path
import pytz
from ruamel.yaml import YAML

from youtube_likes_lib.file_helper import ensure_parent_folder_exists
from youtube_likes_lib.yl_types import Config, StatsSnapshot


yaml = YAML()


@dataclass
class DeltaStats:
    d_hours: float
    d_views: int
    d_likes: int


def get_delta_stats(hours_delta: float, views_log_filepath_templ: str, abbrev: str) -> DeltaStats:
    yaml_filepath = path.expanduser(views_log_filepath_templ.format(abbrev=abbrev))
    with open(yaml_filepath, "r") as f:
        stats = yaml.load(f)
    new_stats = []
    for stat in stats:
        dt = datetime.datetime.strptime(stat["dt"], "%Y%m%d-%H%M")
        dt = dt.replace(tzinfo=pytz.utc)
        hours_old = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
        if hours_old / 3600 > 24 * 3:
            continue
        stat["dt"] = dt
        stat["hours_old"] = hours_old
        stat["delta"] = abs(hours_old - hours_delta)
        new_stats.append(stat)
    stats = new_stats
    new_stat = stats[-1]

    stats.sort(key=lambda stat: stat["delta"])
    old_stat = stats[0]
    d_hours = (new_stat["dt"] - old_stat["dt"]).total_seconds() / 3600
    d_views = new_stat["views"] - old_stat["views"]
    d_likes = new_stat["likes"] - old_stat["likes"]
    print("    d_hours %.1f" % d_hours, "d_views", d_views, "d_likes", d_likes)

    if d_hours > 0:
        d_views = d_views * hours_delta / d_hours
        d_likes = d_likes * hours_delta / d_hours
    else:
        print('warning: d_hours is 0')
        d_views = 0
        d_likes = 0
    print("    d_hours %.1f" % hours_delta, "d_views", d_views, "d_likes", d_likes)

    return DeltaStats(
        d_hours=hours_delta,
        d_views=d_views,
        d_likes=d_likes,
    )
    # return {"d_hours": hours_delta, "d_views": d_views, "d_likes": d_likes}


def write_viewlogs(channel_abbrev: str, persisted: StatsSnapshot, config: Config) -> None:
    view_logfile = path.expanduser(config.views_log_filepath_templ.format(abbrev=channel_abbrev))
    ensure_parent_folder_exists(view_logfile)
    dt = datetime.datetime.now()
    dt_string = dt.strftime("%Y%m%d-%H%M")
    res = {
        "subs": persisted.num_subscriptions,
        "views": persisted.total_views,
        "likes": persisted.total_likes,
        "dt": dt_string
    }
    with open(view_logfile, 'a') as f:
        f.write("- " + json.dumps(res) + "\n")

    video_by_id = {video.video_id: video for video in persisted.videos}
    channel_config_by_abbrev = {config.abbrev: config for config in config.channels}
    channel_config = channel_config_by_abbrev[channel_abbrev]
    for video_id in channel_config.log_videos:
        view_logfile = path.expanduser(config.views_by_video_log_filepath_templ.format(
            abbrev=channel_abbrev, video_id=video_id))
        ensure_parent_folder_exists(view_logfile)
        video = video_by_id[video_id]
        res = {
            "views": video.views,
            "likes": video.likes,
            "comments": video.comments,
            # "favorites": video.favorites,
            "dt": dt_string
        }
        with open(view_logfile, 'a') as f:
            f.write("- " + json.dumps(res) + "\n")
