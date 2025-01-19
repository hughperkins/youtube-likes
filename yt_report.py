"""
To use:
Go to studio analytics for a single video, click on 'Reach' tab, open dev console 'network' section,
refresh page, filter on 'scre', right click the get_screen request, and do 'copy' | Copy as fetch (node.js)
- pasted contents into /tmp/request.js

Outputs csv with:
- video name
- id
- ctr
- views
- likes
- dislikes
- likes_per_k
- dislikes_per_k
"""
import argparse
import csv
from dataclasses import dataclass
import datetime
import json
from typing import Any, Optional, cast

import requests
import chili

import youtube_likes as yl
from youtube_likes_lib.json_wrapper import Json


join_url = "https://studio.youtube.com/youtubei/v1/yta_web/join?alt=json"
join_body_str = "{\"nodes\":[{\"key\":\"0__TOTALS_SUMS_QUERY_KEY\",\"value\":{\"query\":{\"dimensions\":[],\"metrics\":[{\"type\":\"LIKES_PER_LIKES_PLUS_DISLIKES_PERCENT\",\"includeTotal\":true},{\"type\":\"RATINGS_LIKES\",\"includeTotal\":true},{\"type\":\"RATINGS_DISLIKES\",\"includeTotal\":true}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"HI5sjIr9gak\"]}],\"orders\":[],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20241221,\"exclusiveEnd\":20250118}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"1__TOTALS_TIMELINE_QUERY_KEY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"DAY\"}],\"metrics\":[{\"type\":\"LIKES_PER_LIKES_PLUS_DISLIKES_PERCENT\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"HI5sjIr9gak\"]}],\"orders\":[{\"dimension\":{\"type\":\"DAY\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_ASC\"}],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20241221,\"exclusiveEnd\":20250118}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}}],\"connectors\":[],\"allowFailureResultNodes\":true,\"context\":{\"client\":{\"clientName\":62,\"clientVersion\":\"1.20250115.02.00\",\"hl\":\"en\",\"gl\":\"US\",\"experimentsToken\":\"\",\"utcOffsetMinutes\":-300,\"rolloutToken\":\"CLa8vteVgvPM2wEQw8mfzZCWigMYrdHBoZ7_igM%3D\",\"userInterfaceTheme\":\"USER_INTERFACE_THEME_DARK\",\"screenWidthPoints\":1470,\"screenHeightPoints\":474,\"screenPixelDensity\":2,\"screenDensityFloat\":2},\"request\":{\"returnLogEntry\":true,\"internalExperimentFlags\":[],\"eats\":\"Ac1K1YyqRgpIwfyBrUqDTmCFarp3+10mrRbvwMp7mb9Cc+tShOEfV4MfxTDf6hfPD+ZixjGFdcXS6pynPkCyO+ywSF0cWMtzSBCWMyg=\",\"sessionInfo\":{\"token\":\"YR1SZJKFZR\"},\"consistencyTokenJars\":[]},\"user\":{\"onBehalfOfUser\":\"108940515231048981095\",\"delegationContext\":{\"externalChannelId\":\"UCHPoNHk_aC5LmJDDVAH4w7Q\",\"roleType\":{\"channelRoleType\":\"CREATOR_CHANNEL_ROLE_TYPE_OWNER\"}},\"serializedDelegationContext\":\"EhhVQ0hQb05Ia19hQzVMbUpERFZBSDR3N1EqAggI\"},\"clientScreenNonce\":\"PIdrdlQgDFFE02Vs\"},\"trackingLabel\":\"web_explore_video\"}"
join_body = json.loads(join_body_str)

analytics_time_period_by_days = {
    7: "ANALYTICS_TIME_PERIOD_TYPE_WEEK",
    28: "ANALYTICS_TIME_PERIOD_TYPE_FOUR_WEEKS",
    90: "ANALYTICS_TIME_PERIOD_TYPE_QUARTER",
    365: "ANALYTICS_TIME_PERIOD_TYPE_YEAR",
}


@dataclass
class ReportLine:
    title: str
    video_id: str
    views: int
    likes: int
    likes_per_k: int
    dislikes_per_k: int
    ctr: float


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


# def try_Json_class(res):
#     res_json = Json(res.json())
#     # print(res_json)
#     cards = res_json.cards
#     # impressions = cards[0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
#     # impressions = res_json["cards"][0]["keyMetricCardData"]["keyMetricTabs"][0]["primaryContent"]["total"]
#     for i, card in enumerate(cards):
#         print(i, card.keys())
#     key_metric_card_data = get_card2(cards, "keyMetricCardData")["keyMetricCardData"]
#     key_metric_tabs = key_metric_card_data["keyMetricTabs"]
#     print('key_metric_tab:')
#     for key_metric_tab in key_metric_tabs:
#         print('    ', key_metric_tab["metricTabConfig"]["metric"].unwrap_str())
#     impressions = get_metric_total2(key_metric_tabs, "VIDEO_THUMBNAIL_IMPRESSIONS")
#     # vtr is 'view through rate', 
#     # vtr excludes views that are not via a thumbnail, so it is the more accurate measure of ctr,
#     # and matches what is on the youtube web page
#     ctr = get_metric_total2(key_metric_tabs, "VIDEO_THUMBNAIL_IMPRESSIONS_VTR")
#     views = get_metric_total2(key_metric_tabs, "VIEWS")
#     # ctr = views / impressions * 100
#     print('impressions', impressions, 'views', views, f'ctr {ctr:.1f}')
#     # print('views', views, f'ctr {ctr:.1f}')


def load_tab(url: str, headers: Any, body: Any, tab_name: str, video_id: str, days: int) -> Json:
    screen_config = body["screenConfig"]
    screen_config["entity"]["videoId"] = video_id
    screen_config["timePeriod"]["timePeriodType"] = analytics_time_period_by_days[days]
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


def get_metrics(tab_json: Json) -> list[str]:
    cards = tab_json.cards
    key_metric_card_data = get_card2(cards, "keyMetricCardData")["keyMetricCardData"]
    key_metric_tabs = key_metric_card_data["keyMetricTabs"]
    metrics = []
    for keyTab in key_metric_tabs:
        metric = keyTab["metricTabConfig"]["metric"].unwrap_str()
        metrics.append(metric)
    return metrics


def get_metric_total3(tab_json: Json, metric_name: str):
    cards = tab_json.cards
    key_metric_card_data = get_card2(cards, "keyMetricCardData")["keyMetricCardData"]
    key_metric_tabs = key_metric_card_data["keyMetricTabs"]
    v = get_metric_total2(key_metric_tabs, metric_name)
    return v


def get_float_metric_total3(tab_json: Json, metric_name: str) -> float:
    v = get_metric_total3(tab_json=tab_json, metric_name=metric_name)
    v = cast(float, v)
    return v


def get_int_metric_total3(tab_json: Json, metric_name: str) -> int:
    v = get_metric_total3(tab_json=tab_json, metric_name=metric_name)
    v = cast(int, v)
    return v


def get_join_result(join_json_results, join_key: str):
    for r in join_json_results:
        if r["key"] == join_key:
            return r
    raise Exception(f"Could not find join result {join_key}")


def render_join_body(join_body, video_id: str, days: int):
    # print(json.dumps(join_body, indent=2))
    for node in join_body["nodes"]:
        restricts = node["value"]["query"]["restricts"]
        # print('restrict', json.dumps(restricts, indent=2))
        restricts[0]["inValues"][0] = video_id
        date_id_range = node["value"]["query"]["timeRange"]["dateIdRange"]
        # print("date_id_range", date_id_range)
        end_str = datetime.date.today().strftime("%Y%m%d")
        start_str = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y%m%d")
        # print('start_str', start_str, 'end_str', end_str)
        date_id_range["inclusiveStart"] = start_str
        date_id_range["exclusiveEnd"] = end_str
    return join_body


def get_video_stats(get_screen_js: str, video_id: str, title: str, days: int) -> Optional[ReportLine]:
    with open(get_screen_js) as f:
        query_raw = f.read()
    query_json = query_raw.partition(", ")[2].rstrip()[:-2]
    query = json.loads(query_json)
    headers = query["headers"]
    body_str = query["body"]
    body = json.loads(body_str)
    url = query_raw.partition(",")[0].split('"')[1]

    join_body_rendered = render_join_body(join_body, video_id=video_id, days=days)

    join_res = requests.post(join_url, headers=headers, data=json.dumps(join_body_rendered))
    if join_res.status_code >= 300:
        raise Exception("failed", join_res.status_code, join_res.content)
    join_json = join_res.json()
    results = join_json["results"]
    totals = get_join_result(results, "0__TOTALS_SUMS_QUERY_KEY")
    metric_columns = totals["value"]["resultTable"]["metricColumns"]
    likes = metric_columns[1]["counts"].get("total", 0)
    dislikes = metric_columns[2]["counts"].get("total", 0)

    reach_tab = load_tab(
        url=url, headers=headers, body=body, tab_name="ANALYTICS_TAB_ID_REACH", video_id=video_id, days=days)
    metrics = get_metrics(reach_tab)
    if 'SHORTS_FEED_IMPRESSIONS' in metrics:
        print('short => skipping')
        return None

    engagement_tab = load_tab(
        url=url, headers=headers, body=body, tab_name="ANALYTICS_TAB_ID_ENGAGEMENT", video_id=video_id, days=days)
    # metrics = get_metrics(engagement_tab)
    # print(metrics)

    impressions = get_int_metric_total3(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS")
    ctr = get_float_metric_total3(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS_VTR")
    views = get_int_metric_total3(reach_tab, "VIEWS")

    average_watch_time_ms = get_metric_total3(engagement_tab, "AVERAGE_WATCH_TIME")
    average_watch_time = average_watch_time_ms / 1000
    print('likes', likes, 'dislikes', dislikes)
    likes_per_k, dislikes_per_k = 0, 0
    if views > 0:
        likes_per_k = int((likes * 1000) / views)
        dislikes_per_k = int((dislikes * 1000) / views)
    
    print('impressions', impressions, 'ctr', ctr, 'views', views, f'average_watch_time {average_watch_time:.1f}')
    print('likes_per_k', likes_per_k, 'dislikes_per_k', dislikes_per_k)

    report_line = ReportLine(
        title=title,
        video_id=video_id,
        views=views,
        likes=likes,
        likes_per_k=likes_per_k,
        dislikes_per_k=dislikes_per_k,
        ctr=ctr,
    )
    return report_line


def run(args) -> None:
    config = yl.load_config(config_file=args.config_file)
    api_key = config.api_key

    channel_id_by_abbrev = {c.abbrev: c.id for c in config.channels}
    channel_id = channel_id_by_abbrev[args.channel_abbrev]

    _, video_id_names = yl.get_video_id_names_for_channel(api_key=api_key, channel_id=channel_id)
    report_lines = []
    f = open(args.out_csv, 'w')
    dict_writer = csv.DictWriter(f, fieldnames=[
        "title", "video_id", "views", "likes", "likes_per_k", "dislikes_per_k", "ctr"])
    dict_writer.writeheader()
    for video_id_name in video_id_names:
        if args.video_id and video_id_name.video_id != args.video_id:
            continue
        print(video_id_name.video_id, video_id_name.title)
        # print(json.dumps(video_id_name.full_info, indent=2))
        report_line = get_video_stats(
                get_screen_js=args.get_screen_js, video_id=video_id_name.video_id,
                title=video_id_name.title, days=args.days)
        if not report_line:
            continue
        report_lines.append(report_line)
        report_line_dict = chili.asdict(report_line)
        dict_writer.writerow(report_line_dict)
        f.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument('--channel-abbrev', required=True, type=str)
    parser.add_argument('--get-screen-js', default="/tmp/request.js", type=str)
    parser.add_argument('--out-csv', default="/tmp/yt_report.csv", type=str)
    parser.add_argument('--video-id', type=str)
    # parser.add_argument('--time-period', choices=["ANALYTICS_TIME_PERIOD_TYPE_FOUR_WEEKS"])
    parser.add_argument('--days', default=28, type=int, choices=analytics_time_period_by_days.keys())
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
