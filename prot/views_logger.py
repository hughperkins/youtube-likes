# DOESNT WORK, since the stats are not updated by youtube in a timely manner (maybe once a day?)
# use youtube_likes.py to log instead

# log views once an hour, to a yaml file
# so that we can monitor this over time, in a separate script
import argparse
import json
import datetime
import os
from os import path

import requests
from ruamel.yaml import YAML


yaml = YAML()


def process_channel(api_key, channel_id):
    res = requests.get(
        "https://www.googleapis.com/youtube/v3/channels/?id={channel_id}"
        "&part=statistics"
        "&key={api_key}".format(channel_id=channel_id, api_key=api_key)
    )
    if res.status_code != 200:
        print("res.status_code %s" % res.status_code)
        print(res.content)
        raise Exception("invalid status code %s" % res.status_code)
    d = json.loads(res.content.decode("utf-8"))
    print(json.dumps(d, indent=2))
    stats = d["items"][0]["statistics"]
    total_subs = stats["subscriberCount"]
    total_views = stats["viewCount"]
    # persisted["num_subscriptions"] = d["items"][0]["statistics"]["subscriberCount"]
    # print('num_subscriptions %s'
    dt = datetime.datetime.now()
    dt_string = dt.strftime("%Y%m%d-%H%M")
    return {"subs": total_subs, "views": total_views, "dt": dt_string}


def run(args):
    with open(args.config_file, "r") as f:
        config = yaml.load(f)

    api_key = config["api_key"]
    channels = config["channels"]
    channel_id_by_name = {info["name"]: info["id"] for info in channels}
    # channel_name_by_id = {info["id"]: info["name"] for info in channels}
    channel_abbrev_by_id = {info["id"]: info["abbrev"] for info in channels}

    for channel_name, channel_id in channel_id_by_name.items():
        channel_abbrev = channel_abbrev_by_id[channel_id]
        res = process_channel(api_key=api_key, channel_id=channel_id)
        view_logfile = path.expanduser(config['views_log_filepath_templ'].format(channel_abbrev=channel_abbrev))
        view_dir = path.dirname(view_logfile)
        if not path.exists(view_dir):
            os.makedirs(view_dir)
        with open(view_logfile, 'a') as f:
            f.write("- " + json.dumps(res) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    # parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args)
