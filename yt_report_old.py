"""
create a csv file summarizing video perf
"""
import csv
import argparse
from dataclasses import dataclass

import youtube_likes as yl


@dataclass
class ReportLine:
    name: str
    views: int
    likes: int
    likes_per_k: int
    comments_per_100k: int


def run(args: argparse.Namespace) -> None:
    # first, get stats on the videos
    # note that we dont care about num subscribers, total channel views
    # delta changes, etc, just raw video stats
    # (possibly relative to a baseline, or for a specified window of time)

    config = yl.load_config(config_file=args.config_file)
    api_key = config.api_key

    channel_id_by_abbrev = {c.abbrev: c.id for c in config.channels}
    channel_id = channel_id_by_abbrev[args.abbrev]

    stats = yl.get_stats_for_channel(
        config=config, api_key=api_key, channel_abbrev=args.abbrev, channel_id=channel_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--abbrev", help="process only this abbrev")
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
