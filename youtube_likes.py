# Note, if you run this from crontab, you should put the following in front
# of the python command:
# PYTHONIOENCODING=utf-8
# eg
# PYTHONIOENCODING=utf-8 python youtube_likes.py
# (otherwise it won't handle non-latin characters ok)

import argparse
import json
from collections import defaultdict
from typing import Type

import chili
import chili.mapping
from ruamel.yaml import YAML

from youtube_likes_lib import process_logs, email_send_lib, youtube_query_lib, string_lib
from youtube_likes_lib.analyzers import Analyzer, Delta20, Mod100, Mod1000, Pct10
from youtube_likes_lib.cache_mgr import get_mins_since_last_write, load_cache, write_cache
from youtube_likes_lib.view_logs import write_viewlogs
from youtube_likes_lib.yl_types import Channel, Config, Output, StatsSnapshot, Video


yaml = YAML()

# warnings.simplefilter("ignore", yaml.error.UnsafeLoaderWarning)


g_delta_views_threshold_pct_by_delta_hours = {
    8: 40,
    24: 20,
    48: 10,
}


def get_video_ids_for_channel(api_key: str, channel_id: str) -> tuple[int, list[str]]:
    uploads_playlist_id, num_subscriptions = youtube_query_lib.get_uploads_playlist_id_and_subscribers(
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
    return num_subscriptions, video_ids


def get_video_stats(api_key: str, video_ids: list[str]) -> list[Video]:
    videos = youtube_query_lib.get_videos(
        api_key=api_key,
        video_ids=video_ids,
    )

    print('')
    print('Get stats for each video:')
    video_infos: list[Video] = []
    # total_views = 0
    # total_likes = 0
    for video in videos:
        if "short" in video["snippet"].get("tags", []):
            print(f"- [skip short \"{video['snippet']['title']}\"]")
            continue
        video_id = video["id"]
        title = video["snippet"]["title"]
        s = video["statistics"]
        # print(s)
        likes = int(s.get("likeCount", 0))
        views = int(s.get("viewCount", 0))
        # total_views += views
        # total_likes += likes
        print(f"- {title} views {views}")
        # favorites = int(s.get("favoriteCount", 0))
        comments = int(s.get("commentCount", 0))
        video_infos.append(
            Video(
                video_id=video_id,
                title=title,
                views=views,
                likes=likes,
                comments=comments,
            ))
    return video_infos


def get_stats_for_channel(
        config: Config, api_key: str, channel_id: str, channel_abbrev: str) -> StatsSnapshot:
    # persisted: Dict[str, Any] = {}
    """
    Gets all video ids for the channel, along with the number of subscriptions
    then populates the returned dictionary with a list of Videos
    """

    num_subscriptions, video_ids = get_video_ids_for_channel(
        api_key=api_key, channel_id=channel_id
    )

    video_infos = get_video_stats(api_key=api_key, video_ids=video_ids)
    total_views = sum([v.views for v in video_infos])
    total_likes = sum([v.likes for v in video_infos])
    # persisted["videos"] = video_infos
    # persisted["total_views"] = total_views
    # persisted["total_likes"] = total_likes
    delta_by_time = {}
    for d_hours in [8, 24, 48]:
        _res = process_logs.get_delta_stats(
            hours_delta=d_hours,
            views_log_filepath_templ=config.views_log_filepath_templ,
            abbrev=channel_abbrev,
        )
        # print(_res)
        delta_by_time[d_hours] = _res
        # persisted[f"delta{d_hours}"] = _res
    print('total_views', total_views, 'total_likes', total_likes)
    stats_snapshot = StatsSnapshot(
        videos=video_infos,
        num_subscriptions=num_subscriptions,
        delta_by_time=delta_by_time,
        total_views=total_views,
        total_likes=total_likes,
    )
    return stats_snapshot


def analyse_video(
        channel_config: Channel, channel_abbrev: str, old_video: Video, new_video: Video,
        analyzer_classes: list[Type[Analyzer]],
) -> Output:
    video_title = new_video.title
    video_id = new_video.video_id

    stats_baselines = channel_config.stats_baselines
    stats_baseline = stats_baselines.get(video_id, defaultdict(int))

    output = Output()

    if not analyzer_classes:
        analyzer_classes = []
    analysers = [AnalyzerClass(channel_abbrev=channel_abbrev, output=output) for AnalyzerClass in analyzer_classes]

    # for k in new_video.keys():
    # old_video_dict = old_video.__dict__
    # new_video_dict = new_video.__dict__
    # for k in new_video_dict.keys():
    for k in ["comments", "likes", "views"]:
        if (
            k == "comments"
            and video_title == "2 Create Unity RL env WITHOUT mlagents!"
            and getattr(new_video, k, 0) <= 2
        ):
            continue

        if k not in ["likes", "comments", "views"]:
            continue
        _old_value = getattr(old_video, k, 0)
        _new_value = getattr(new_video, k, 0)
        _old_value -= stats_baseline.get(k, 0)
        _new_value -= stats_baseline.get(k, 0)
        _change = _new_value - _old_value
        _chg_str = string_lib.int_to_signed_str(_change)
        if getattr(old_video, k) != getattr(new_video, k):
            output.body += f"  {k} {_chg_str} => {_new_value}\n"

            if (
                k in ["views", "likes", "comments"]
                and _new_value > _old_value
            ):
                _letter = {"views": "v", "comments": "c", "likes": "l"}[k]
                for analyser in analysers:
                    analyser(video_title=video_title, _old_value=_old_value, _new_value=_new_value, _letter=_letter)
    return output


def compare_video_lists(
    output: Output, channel_config: Channel, channel_abbrev: str,
    old_videos: list[Video], new_videos: list[Video],
    analyzer_classes: list[Type[Analyzer]],
):
    old_by_id = {v.video_id: v for v in old_videos}
    new_by_id = {v.video_id: v for v in new_videos}
    for video_id, video in new_by_id.items():
        if video_id not in old_by_id:
            output.body += "new:\n"
            output.body += json.dumps(chili.asdict(video), indent=2) + "\n"
        else:
            old_video = old_by_id[video_id]
            analysis = analyse_video(
                channel_abbrev=channel_abbrev, new_video=video, old_video=old_video,
                channel_config=channel_config,
                analyzer_classes=analyzer_classes)
            _body = analysis.body
            if _body.strip() != "":
                output.body += video.title + ":\n"
                print(f'_body [{_body}]')
                output.body += _body[:-1] + "\n"
            output.priority_reasons_title += analysis.priority_reasons_title
            output.priority_reasons_desc += analysis.priority_reasons_desc
            output.is_priority = output.is_priority or analysis.is_priority


def process_channel(channel_id: str, channel_abbrev: str, api_key: str, config: Config):
    channels = config.channels
    channel_name_by_id = {info.id: info.name for info in channels}
    channel_config_by_id = {channel_config.id: channel_config for channel_config in channels}
    channel_name = channel_name_by_id[channel_id]

    print('')
    print('============================================================')
    print(channel_abbrev)
    print(channel_name)
    print('')
    new_persisted = get_stats_for_channel(
        config=config, api_key=api_key, channel_id=channel_id, channel_abbrev=channel_abbrev)

    write_viewlogs(channel_abbrev=channel_abbrev, persisted=new_persisted, config=config)

    old_persisted = load_cache(config=config, channel_abbrev=channel_abbrev)

    output = Output()

    videos = new_persisted.videos
    old_videos = old_persisted.videos
    compare_video_lists(
        old_videos=old_videos, new_videos=videos, channel_config=channel_config_by_id[channel_id],
        channel_abbrev=channel_abbrev, output=output,
        analyzer_classes=[Mod100, Mod1000, Pct10, Delta20])

    if new_persisted.num_subscriptions != old_persisted.num_subscriptions:
        output.is_priority = True
        output.priority_reasons_title += " sub"
        output.priority_reasons_desc += f'- Subs {old_persisted.num_subscriptions} => {new_persisted.num_subscriptions}\n'
        output.body += (
            "num subscriptions: %s => %s"
            % (old_persisted.num_subscriptions, new_persisted.num_subscriptions)
            + "\n"
        )

    show_d8 = True
    show_d24 = True
    show_d48 = True

    if channel_abbrev not in ['RL']:
        show_d8 = False
        show_d24 = False
        show_d48 = False

    if (
        (48 in old_persisted.delta_by_time) and
        (48 in new_persisted.delta_by_time) and
        (old_persisted.delta_by_time[48].d_views < 1000) and
        (new_persisted.delta_by_time[48].d_views < 1000)
    ):
        show_d8 = False

    def run_check(output: Output, d_hours: int, can_prioritize: bool) -> None:
        print(f'checking changes h_hours {d_hours}')
        # _delta_key = f"delta{d_hours}"
        # print(f'_delta_key {_delta_key}')
        if d_hours in old_persisted.delta_by_time and d_hours in new_persisted.delta_by_time:
            print(f'{d_hours} in both old and new')
            old_d_views = old_persisted.delta_by_time[d_hours].d_views
            new_d_views = new_persisted.delta_by_time[d_hours].d_views
            d_views_diff = new_d_views - old_d_views
            print(f'd_views_diff {d_views_diff:.0f}')
            d_views_diff_pct = 0.0
            if new_d_views > 0:
                d_views_diff_pct = d_views_diff / new_d_views * 100
            print(f'd_views_diff_pct {d_views_diff_pct:.0f}')
            if abs(d_views_diff_pct) > g_delta_views_threshold_pct_by_delta_hours[d_hours] and can_prioritize:
                print('is_priority')
                output.is_priority = True
                output.priority_reasons_title += f" DV{d_hours}"
                output.priority_reasons_desc += f"- Delta views pct {d_hours}h {g_delta_views_threshold_pct_by_delta_hours[d_hours]}%: {old_d_views:.0f} => {new_d_views:.0f}\n"
            if abs(d_views_diff_pct) > 0:
                output.body += f"- Delta views pct {d_hours}h: {old_d_views:.0f} => {new_d_views:.0f}\n"

    run_check(output, 8, show_d8)
    run_check(output, 24, show_d24)
    run_check(output, 48, show_d48)

    mins_since_last_write = get_mins_since_last_write(config=config, channel_abbrev=channel_abbrev)

    print(f'output_str [{output.body}]')

    email_send_lib.generate_email_message(channel_name=channel_name, channel_abbrev=channel_abbrev, output=output)

    return {
        "channel_name": channel_name,
        "channel_abbrev": channel_abbrev,
        "output": output,
        "persisted": new_persisted,
        "mins_since_last_write": mins_since_last_write,
    }


def run(args) -> None:
    with open(args.config_file, "r") as f:
        config_dict = yaml.load(f)
    config = chili.init_dataclass(config_dict, Config)

    api_key = config.api_key
    channels = config.channels
    channel_id_by_name = {info.name: info.id for info in channels}
    channel_abbrev_by_id = {info.id: info.abbrev for info in channels}

    results = []

    for _, channel_id in channel_id_by_name.items():
        channel_abbrev = channel_abbrev_by_id[channel_id]

        if args.abbrev is not None:
            if channel_abbrev.lower() != args.abbrev.lower():
                continue

        res = process_channel(channel_id=channel_id, channel_abbrev=channel_abbrev, api_key=api_key, config=config)
        # output_by_abbrev[channel_abbrev] = res
        results.append(res)

    outputs = [res["output"] for res in results]

    global_priority_reasons_title, global_email_message = email_send_lib.merge_channel_mails(outputs)
    if global_email_message == "":
        print("No changes detected")
        return

    global_is_priority = any([res["output"].is_priority for res in results])
    if args.priority:
        global_is_priority = True
    print("global_priority", global_is_priority)

    # global_priority_reasons_title = " ".join([res["output"].priority_reasons_title for res in results])
    print('')
    print("Subject: ", global_priority_reasons_title)
    print('')
    print(global_email_message)
    print('(end of email)')

    global_mins_since_last_write = max([res["mins_since_last_write"] for res in results])
    print(f'global_mins_since_last_write {global_mins_since_last_write:.1f}')
    if (
        not global_is_priority
        and global_mins_since_last_write < config.min_change_interval_minutes
    ):
        print(
            "skipping, since only %.1f" % global_mins_since_last_write, "mins since last write"
        )
        return

    if config.send_smtp and not args.no_send_email:
        email_send_lib.send_smtp(config=config, subject_postfix=global_priority_reasons_title, body=global_email_message)

    if not args.no_update_cache:
        for res in results:
            channel_abbrev = res["channel_abbrev"]
            write_cache(config=config, channel_abbrev=channel_abbrev, persisted=res["persisted"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--no-send-email", action="store_true")
    parser.add_argument("--no-update-cache", action="store_true")
    parser.add_argument("--abbrev", help="process only this abbrev")
    parser.add_argument("--priority", action="store_true")
    args = parser.parse_args()
    run(args)
