import argparse
import datetime
import json
import pytz
from ruamel.yaml import YAML
from os.path import expanduser as expand


yaml = YAML()


def get_delta_stats(hours_delta: float, views_log_filepath_templ: str, abbrev: str):
    yaml_filepath = expand(views_log_filepath_templ.format(abbrev=abbrev))
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

    return {"d_hours": hours_delta, "d_views": d_views, "d_likes": d_likes}


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
