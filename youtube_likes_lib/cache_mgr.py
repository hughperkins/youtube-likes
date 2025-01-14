import math
from os import path
import time

import chili
from ruamel.yaml import YAML
from youtube_likes_lib.yl_types import Config, StatsSnapshot


yaml = YAML()


def get_cache_filepath(config: Config, channel_abbrev: str) -> str:
    cache_file_path_templ = config.cache_file_path_templ
    cache_file_path = path.expanduser(cache_file_path_templ.format(abbrev=channel_abbrev))
    return cache_file_path


def load_cache(config: Config, channel_abbrev: str) -> StatsSnapshot:
    cache_file_path = get_cache_filepath(config=config, channel_abbrev=channel_abbrev)
    if path.isfile(cache_file_path):
        with open(cache_file_path, "r") as f:
            as_dict = yaml.load(f)
        # print(as_dict)
        if "delta_by_time" not in as_dict:
            as_dict["delta_by_time"] = {}
        old_persisted = chili.init_dataclass(as_dict, StatsSnapshot)
        # old_persisted = chili.extract(as_dict, StatsSnapshot)
        # json_str = f.read()
        # old_persisted = chili.from_json(json_str, StatsSnapshot)
    else:
        old_persisted = StatsSnapshot(
            num_subscriptions=0,
            videos=[],
            total_likes=0,
            total_views=0,
            delta_by_time={},
        )
    return old_persisted


def write_cache(config: Config, channel_abbrev: str, persisted: StatsSnapshot) -> None:
    cache_file_path = get_cache_filepath(config=config, channel_abbrev=channel_abbrev)
    cache_dir = path.dirname(cache_file_path)
    if not path.exists(cache_dir):
        os.makedirs(cache_dir)
    as_dict = chili.asdict(persisted)
    with open(cache_file_path, "w") as f:
        yaml.dump(as_dict, f)
        print(f' wrote {cache_file_path}')


def get_mins_since_last_write(config: Config, channel_abbrev: str) -> float:
    cache_file_path = get_cache_filepath(config=config, channel_abbrev=channel_abbrev)
    if path.exists(cache_file_path):
        mins_since_last_write = (time.time() - path.getmtime(cache_file_path)) / 60
    else:
        mins_since_last_write = math.inf
    return mins_since_last_write
