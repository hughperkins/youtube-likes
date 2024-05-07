import argparse
import datetime
import json
import pytz
from ruamel.yaml import YAML
from os.path import expanduser as expand


yaml = YAML()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--abbrev", default="RL")
    parser.add_argument("--hours-delta", type=int, default=12)
    parser.add_argument("--view-logs-file-templ", default=expand("~/views_logs/views_log_{abbrev}.yaml"))
    args = parser.parse_args()

    yaml_filepath = args.view_logs_file_templ.format(abbrev=args.abbrev)
    with open(yaml_filepath, "r") as f:
        stats = yaml.load(f)
    # print(json.dumps(stats, indent=2))
    new_stats = []
    for stat in stats:
        dt = datetime.datetime.strptime(stat["dt"], "%Y%m%d-%H%M")
        dt = dt.replace(tzinfo=pytz.utc)
        hours_old = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
        if hours_old / 3600 > 24 * 3:
            continue
        stat["dt"] = dt
        stat["hours_old"] = hours_old
        stat["delta"] = abs(hours_old - args.hours_delta)
        new_stats.append(stat)
    stats = new_stats
    new_stat = stats[-1]

    # print("")
    # for stat in stats:
    #     print(stat)

    # print("")
    stats.sort(key=lambda stat: stat["delta"])
    old_stat = stats[0]
    # print(old_stat)
    # print(new_stat)
    d_hours = (new_stat["dt"] - old_stat["dt"]).total_seconds() / 3600
    # print('d_hours', d_hours)
    d_views = new_stat["views"] - old_stat["views"]
    d_likes = new_stat["likes"] - old_stat["likes"]
    print("d_hours %.1f" % d_hours, "d_views", d_views, "d_likes", d_likes)

    d_views = d_views * args.hours_delta / d_hours
    d_likes = d_likes * args.hours_delta / d_hours
    print("d_hours %.1f" % args.hours_delta, "d_views", d_views, "d_likes", d_likes)

    # best_
    # for stat in stats:
    #     print(stat)
    # print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
