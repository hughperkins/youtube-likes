# Note, if you run this from crontab, you should put the following in front
# of the python command:
# PYTHONIOENCODING=utf-8
# eg
# PYTHONIOENCODING=utf-8 python youtube_likes.py
# (otherwise it won't handle non-latin characters ok)

import argparse
from os.path import expanduser

from ruamel.yaml import YAML
import chili

import youtube_likes
import youtube_likes as yl


yaml = YAML()


def run(args) -> None:
    with open(args.config_file, "r") as f:
        config_dict = yaml.load(f)
    config = chili.init_dataclass(config_dict, yl.Config)
    config.cache_file_path_templ = args.cache_file_path_templ

    api_key = config.api_key
    channels = config.channels
    channel_id_by_name = {info.name: info.id for info in channels}
    channel_abbrev_by_id = {info.id: info.abbrev for info in channels}
    channel_config_by_id = {info.id: info for info in channels}

    # results = []

    videos_by_channel_abbrev: dict[str, list[yl.Video]] = {}
    output_by_channel_abbrev: dict[str, yl.Output] = {}
    for _, channel_id in channel_id_by_name.items():
        channel_abbrev = channel_abbrev_by_id[channel_id]

        if args.abbrev is not None:
            if channel_abbrev.lower() != args.abbrev.lower():
                continue
        channel_config = channel_config_by_id[channel_id]
        # channel_name = channel_config.name
        old_persisted = youtube_likes.load_cache(config=config, channel_abbrev=channel_abbrev)
        video_ids = [v["id"] for v in channel_config.specific_videos]
        videos = youtube_likes.get_video_stats(api_key=api_key, video_ids=video_ids)
        videos_by_channel_abbrev[channel_abbrev] = videos
        
        # youtube_likes.analyse_video(
        #     channel_config=channel_config, channel_abbrev=channel_abbrev,
        #     old_video=)
        # for video_id in channel_config.get("specific_videos", []):

        # videos = new_persisted.videos
        old_videos = old_persisted.videos
        output = yl.Output()
        yl.compare_video_lists(
            old_videos=old_videos, new_videos=videos, channel_config=channel_config_by_id[channel_id],
            channel_abbrev=channel_abbrev, output=output,
            analyzer_classes=[yl.Mod100, yl.Mod1000, yl.Pct10, yl.Delta20])
        print(output.body)
        output_by_channel_abbrev[channel_abbrev] = output

    global_email_title, global_email_body = yl.merge_channel_mails(list(output_by_channel_abbrev.values()))

    if global_email_body.strip() == "":
        print("no change")
        return

    if config.send_smtp and not args.no_send_email:
        yl.send_smtp(config=config, subject_postfix=global_email_title, body=global_email_body)

    if not args.no_update_cache:
        for channel_abbrev, videos in videos_by_channel_abbrev.items():
            if len(videos) == 0:
                continue
            old_persisted = youtube_likes.load_cache(config=config, channel_abbrev=channel_abbrev)
            old_videos = old_persisted.videos
            old_video_n_by_id = {v.video_id: i for i, v in enumerate(old_videos)}
            for v in videos:
                if v.video_id in old_video_n_by_id:
                    n = old_video_n_by_id[v.video_id]
                    old_videos[n] = v
                else:
                    old_videos.append(v)
            # channel_abbrev = res["channel_abbrev"]
            yl.write_cache(config=config, channel_abbrev=channel_abbrev, persisted=old_persisted)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--no-send-email", action="store_true")
    parser.add_argument("--no-update-cache", action="store_true")
    parser.add_argument("--abbrev", help="process only this abbrev")
    parser.add_argument("--cache-file-path-templ", default=expanduser("~/youtube_views_cache/cache_specific_{abbrev}.txt"))
    args = parser.parse_args()
    run(args)
