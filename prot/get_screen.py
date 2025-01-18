"""
Go to studio analytics for a single video, click on 'Reach' tab, open dev console 'network' section,
refresh page, filter on 'scre', right click the get_screen request, and do 'copy' | Copy as fetch (node.js)
- pasted contents into /tmp/request.js
"""
import argparse
import json
from typing import Any, cast
import requests


JSON = dict[str, 'JSON'] | list['JSON'] | str | int | None | float


class Json:
    def __init__(self, data: JSON):
        self.data = data
    
    def __getattr__(self, k: str) -> 'Json':
        return Json(cast(dict[str, JSON], self.data)[k])

    def __getitem__(self, i: int | str) -> 'Json':
        if isinstance(i, int):
            res = cast(list[JSON], self.data)[i]
            # if isinstance(res, list) or isinstance(res, dict):
            return Json(res)
            # return res
        else:
            return Json(cast(dict[str, JSON], self.data)[i])
    
    def unwrap_int(self) -> int:
        return cast(int, self.data)

    def unwrap_str(self) -> str:
        return cast(str, self.data)

    def __iter__(self):
        # print('__iter__')
        for child in cast(list[JSON], self.data):
            yield Json(child)
    
    def keys(self) -> list[str]:
        return list(cast(dict[str, JSON], self.data).keys())
    
    def __contains__(self, k) -> bool:
        # print('__contains__', k)
        return k in cast(dict[str, JSON], self.data)


def get_card2(cards: Json, cardName: str) -> Json:
    for card in cards:
        if cardName in card:
            return card
    raise Exception(f"card {cardName} not found")


def get_metric_tab2(key_metric_tabs: Json, tab_name: str) -> Json:
    for keyTab in key_metric_tabs:
        if keyTab["metricTabConfig"]["metric"].unwrap_str() == tab_name:
            return keyTab
    raise Exception(f"metric tab {tab_name} not found")


def get_metric_total2(key_metric_tabs: Json, metric_name: str) -> int | float:
    metric_tab = get_metric_tab2(key_metric_tabs=key_metric_tabs, tab_name=metric_name)
    total = metric_tab["primaryContent"]["total"].unwrap_int()
    return total


def try_Json_class(res):
    res_json = Json(res.json())
    # print(res_json)
    cards = res_json.cards
    # impressions = cards[0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
    # impressions = res_json["cards"][0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
    for i, card in enumerate(cards):
        print(i, card.keys())
    key_metric_card_data = get_card2(cards, "keyMetricCardData")["keyMetricCardData"]
    key_metric_tabs = key_metric_card_data["keyMetricTabs"]
    print('key_metric_tab:')
    for key_metric_tab in key_metric_tabs:
        print('    ', key_metric_tab["metricTabConfig"]["metric"].unwrap_str())
    impressions = get_metric_total2(key_metric_tabs, "VIDEO_THUMBNAIL_IMPRESSIONS")
    # vtr is 'view through rate', 
    # vtr excludes views that are not via a thumbnail, so it is the more accurate measure of ctr,
    # and matches what is on the youtube web page
    ctr = get_metric_total2(key_metric_tabs, "VIDEO_THUMBNAIL_IMPRESSIONS_VTR")
    views = get_metric_total2(key_metric_tabs, "VIEWS")
    # ctr = views / impressions * 100
    print('impressions', impressions, 'views', views, f'ctr {ctr:.1f}')


def load_tab(url: str, headers: Any, body: Any, tab_name: str, video_id: str) -> Json:
    screen_config = body["screenConfig"]
    screen_config["entity"]["videoId"] = video_id
    # print(json.dumps(screen_config, indent=2))
    desktop_state = body["desktopState"]
    # ANALYTICS_TAB_ID_REACH
    # ANALYTICS_TAB_ID_ENGAGEMENT
    desktop_state["tabId"] = tab_name
    # print(json.dumps(desktop_state, indent=2))
    body_str = json.dumps(body)
    res = requests.post(url, headers=headers, data=body_str)
    if res.status_code >= 300:
        raise Exception('ERROR', res, res.json())
    return Json(res.json())


def get_metric_total3(tab_json: Json, metric_name: str):
    # res_json = Json(res.json())
    # print(res_json)
    cards = tab_json.cards
    # impressions = cards[0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
    # impressions = res_json["cards"][0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
    key_metric_card_data = get_card2(cards, "keyMetricCardData")["keyMetricCardData"]
    key_metric_tabs = key_metric_card_data["keyMetricTabs"]
    # print('key_metric_tab:')
    # for key_metric_tab in key_metric_tabs:
    #     print('    ', key_metric_tab["metricTabConfig"]["metric"].unwrap_str())
    # print('key_metric_tab:')
    # for key_metric_tab in key_metric_tabs:
    #     print('    ', key_metric_tab["metricTabConfig"]["metric"].unwrap_str())
    v = get_metric_total2(key_metric_tabs, metric_name)
    return v


def run(args) -> None:
    with open(args.get_screen_js) as f:
        query_raw = f.read()
    query_json = query_raw.partition(", ")[2].rstrip()[:-2]
    query = json.loads(query_json)
    headers = query["headers"]
    body_str = query["body"]
    body = json.loads(body_str)
    url = query_raw.partition(",")[0].split('"')[1]

    # screen_config = body["screenConfig"]
    # screen_config["entity"]["videoId"] = args.video_id
    # print(json.dumps(screen_config, indent=2))
    # desktop_state = body["desktopState"]
    # ANALYTICS_TAB_ID_REACH
    # ANALYTICS_TAB_ID_ENGAGEMENT
    # desktop_state["tabId"] = "ANALYTICS_TAB_ID_ENGAGEMENT"
    # print(json.dumps(desktop_state, indent=2))
    # body_str = json.dumps(body)
    # res = requests.post(url, headers=headers, data=body_str)
    # if res.status_code >= 300:
    #     print('ERROR', res, res.json())
    #     return
    # try_Json_class(res)

    reach_tab = load_tab(url=url, headers=headers, body=body, tab_name="ANALYTICS_TAB_ID_REACH", video_id=args.video_id)
    engagement_tab = load_tab(url=url, headers=headers, body=body, tab_name="ANALYTICS_TAB_ID_ENGAGEMENT", video_id=args.video_id)

    impressions = get_metric_total3(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS")
    ctr = get_metric_total3(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS_VTR")
    views = get_metric_total3(reach_tab, "VIEWS")

    # watch_time_ms = get_metric_total3(engagement_tab, "WATCH_TIME")
    average_watch_time_ms = get_metric_total3(engagement_tab, "AVERAGE_WATCH_TIME")
    average_watch_time = average_watch_time_ms / 1000
    # print('average_watch_time', average_watch_time_ms, 'watch_time', watch_time_ms)
    print('impressions', impressions, 'ctr', ctr, 'views', views, f'average_watch_time {average_watch_time:.1f}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--get-screen-js', default="/tmp/request.js", type=str)
    parser.add_argument('--video-id', required=True, type=str)
    parser.add_argument('--time-period', choices=["ANALYTICS_TIME_PERIOD_TYPE_FOUR_WEEKS"])
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
