import argparse
from os.path import expanduser as expand

from youtube_likes_lib.view_logs import get_delta_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--abbrev", default="RL")
    parser.add_argument("--hours-delta", type=int, default=12)
    parser.add_argument("--views-logs-file-templ", default=expand("~/views_logs/views_log_{abbrev}.yaml"))
    args = parser.parse_args()

    stats = get_delta_stats(
        hours_delta=args.hours_delta, views_log_filepath_templ=args.view_logs_file_templ, abbrev=args.abbrev)
    print(stats)


if __name__ == '__main__':
    main()
