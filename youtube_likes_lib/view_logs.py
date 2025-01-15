import datetime
import json
from os import path
import pytz
from ruamel.yaml import YAML

from youtube_likes_lib.file_helper import ensure_parent_folder_exists
from youtube_likes_lib.yl_types import Config, DeltaStats, Output, StatsSnapshot


yaml = YAML()


g_delta_views_threshold_pct_by_delta_hours = {
    8: 40,
    24: 20,
    48: 10,
}


class DeltaChecker():
    def __init__(self, old_persisted: StatsSnapshot, new_persisted: StatsSnapshot, output: Output) -> None:
        self.old_persisted = old_persisted
        self.new_persisted = new_persisted
        self.output = output

    def run_check(self, d_hours: int, can_prioritize: bool) -> None:
        print(f'checking changes h_hours {d_hours}')
        if d_hours in self.old_persisted.delta_by_time and d_hours in self.new_persisted.delta_by_time:
            print(f'{d_hours} in both old and new')
            old_d_views = self.old_persisted.delta_by_time[d_hours].d_views
            new_d_views = self.new_persisted.delta_by_time[d_hours].d_views
            d_views_diff = new_d_views - old_d_views
            print(f'd_views_diff {d_views_diff:.0f}')
            d_views_diff_pct = 0.0
            if new_d_views > 0:
                d_views_diff_pct = d_views_diff / new_d_views * 100
            print(f'd_views_diff_pct {d_views_diff_pct:.0f}')
            if abs(d_views_diff_pct) > g_delta_views_threshold_pct_by_delta_hours[d_hours] and can_prioritize:
                print('is_priority')
                self.output.is_priority = True
                self.output.priority_reasons_title += f" DV{d_hours}"
                self.output.priority_reasons_desc += (
                    f"- Delta views pct {d_hours}h {g_delta_views_threshold_pct_by_delta_hours[d_hours]}%: "
                    f"{old_d_views:.0f} => {new_d_views:.0f}\n"
                )
            if abs(d_views_diff_pct) > 0:
                self.output.body += f"- Delta views pct {d_hours}h: {old_d_views:.0f} => {new_d_views:.0f}\n"


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
