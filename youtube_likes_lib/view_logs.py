from dataclasses import dataclass
import datetime
import json
from os import path
import pytz
from ruamel.yaml import YAML
import chili

from youtube_likes_lib.file_helper import ensure_parent_folder_exists
from youtube_likes_lib.yl_types import ChannelStatsLogLine, Config, DeltaStats, Output, VideoStatsLogLine, StatsSnapshot, Video


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


def datetime_str_to_datetime(datetime_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(datetime_str, "%Y%m%d-%H%M")


def get_delta_stats(hours_delta: float, views_log_filepath_templ: str, abbrev: str) -> DeltaStats:
    """
    Load logfiles, and find the logentry closest in time to hours_delta ago, and compare that
    to the log entry for now, and return this delta
    """
    yaml_filepath = path.expanduser(views_log_filepath_templ.format(abbrev=abbrev))
    with open(yaml_filepath, "r") as f:
        stats = yaml.load(f)

    @dataclass
    class LogLineDelta:
        delta_hours: float
        stat: ChannelStatsLogLine

    stat_delta_l: list[LogLineDelta] = []
    for stat_d in stats:
        stat = chili.init_dataclass(stat_d, ChannelStatsLogLine)
        dt = datetime_str_to_datetime(stat.dt)
        dt = dt.replace(tzinfo=pytz.utc)
        hours_old = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
        if hours_old / 3600 > 24 * 3:
            continue
        delta = abs(hours_old - hours_delta)
        stat_delta_l.append(LogLineDelta(delta_hours=delta, stat=stat))
    new_stat = stat_delta_l[-1].stat

    stat_delta_l.sort(key=lambda logline_delta: logline_delta.delta_hours)
    old_stat = stat_delta_l[0].stat
    new_dt = datetime_str_to_datetime(new_stat.dt)
    old_dt = datetime_str_to_datetime(old_stat.dt)
    d_hours = (new_dt - old_dt).total_seconds() / 3600
    d_views = new_stat.views - old_stat.views
    d_likes = new_stat.likes - old_stat.likes
    print("    d_hours %.1f" % d_hours, "d_views", d_views, "d_likes", d_likes)

    if d_hours > 0:
        d_views = int(d_views * hours_delta / d_hours)
        d_likes = int(d_likes * hours_delta / d_hours)
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


def get_datetime_str(dt: datetime.datetime) -> str:
    dt_string = dt.strftime("%Y%m%d-%H%M")
    return dt_string


def write_channel_logline(dt: datetime.datetime, channel_abbrev: str, config: Config, persisted: StatsSnapshot) -> None:
    view_logfile = path.expanduser(config.views_log_filepath_templ.format(abbrev=channel_abbrev))
    dt_string = get_datetime_str(dt=dt)
    ensure_parent_folder_exists(view_logfile)
    res = ChannelStatsLogLine(
        dt=dt_string,
        subs=persisted.num_subscriptions,
        views=persisted.total_views,
        likes=persisted.total_likes
    )
    res_str = chili.as_json(res, ChannelStatsLogLine)
    with open(view_logfile, 'a') as f:
        f.write("- " + res_str + "\n")


def write_video_logline(dt: datetime.datetime, config: Config, channel_abbrev: str, video: Video) -> None:
    dt_string = get_datetime_str(dt=dt)
    view_logfile = path.expanduser(config.views_by_video_log_filepath_templ.format(
        abbrev=channel_abbrev, video_id=video.video_id))
    ensure_parent_folder_exists(view_logfile)
    res = VideoStatsLogLine(
        views=video.views,
        likes=video.likes,
        comments=video.comments,
        dt=dt_string
    )
    res_str = chili.as_json(res, VideoStatsLogLine)
    with open(view_logfile, 'a') as f:
        f.write("- " + res_str + "\n")


def write_per_video_loglines(dt: datetime.datetime, channel_abbrev: str, config: Config, persisted: StatsSnapshot) -> None:
    video_by_id = {video.video_id: video for video in persisted.videos}
    channel_config_by_abbrev = {config.abbrev: config for config in config.channels}
    channel_config = channel_config_by_abbrev[channel_abbrev]
    for video_id in channel_config.log_videos:
        if video_id not in video_by_id:
            return
        video = video_by_id[video_id]
        write_video_logline(video=video, channel_abbrev=channel_abbrev, config=config, dt=dt)


def write_viewlogs(channel_abbrev: str, persisted: StatsSnapshot, config: Config) -> None:
    """
    Writes a line in the channel logfile, for subs, views, likes, date
    for each video in log_videos, from config, writes a line to video-specific
    file, with views, likes, comments
    """
    dt = datetime.datetime.now()
    write_channel_logline(dt=dt, channel_abbrev=channel_abbrev, persisted=persisted, config=config)
    write_per_video_loglines(dt=dt, channel_abbrev=channel_abbrev, persisted=persisted, config=config)
