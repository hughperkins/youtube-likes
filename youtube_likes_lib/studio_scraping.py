import datetime
import json
from typing import Any, cast

import requests

from youtube_likes_lib.json_wrapper import Json


join_url = "https://studio.youtube.com/youtubei/v1/yta_web/join?alt=json"
join_body_str = "{\"nodes\":[{\"key\":\"0__TOTALS_SUMS_QUERY_KEY\",\"value\":{\"query\":{\"dimensions\":[],\"metrics\":[{\"type\":\"LIKES_PER_LIKES_PLUS_DISLIKES_PERCENT\",\"includeTotal\":true},{\"type\":\"RATINGS_LIKES\",\"includeTotal\":true},{\"type\":\"RATINGS_DISLIKES\",\"includeTotal\":true}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"HI5sjIr9gak\"]}],\"orders\":[],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20241221,\"exclusiveEnd\":20250118}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}},{\"key\":\"1__TOTALS_TIMELINE_QUERY_KEY\",\"value\":{\"query\":{\"dimensions\":[{\"type\":\"DAY\"}],\"metrics\":[{\"type\":\"LIKES_PER_LIKES_PLUS_DISLIKES_PERCENT\"}],\"restricts\":[{\"dimension\":{\"type\":\"VIDEO\"},\"inValues\":[\"HI5sjIr9gak\"]}],\"orders\":[{\"dimension\":{\"type\":\"DAY\"},\"direction\":\"ANALYTICS_ORDER_DIRECTION_ASC\"}],\"timeRange\":{\"dateIdRange\":{\"inclusiveStart\":20241221,\"exclusiveEnd\":20250118}},\"currency\":\"USD\",\"returnDataInNewFormat\":true,\"limitedToBatchedData\":false}}}],\"connectors\":[],\"allowFailureResultNodes\":true,\"context\":{\"client\":{\"clientName\":62,\"clientVersion\":\"1.20250115.02.00\",\"hl\":\"en\",\"gl\":\"US\",\"experimentsToken\":\"\",\"utcOffsetMinutes\":-300,\"rolloutToken\":\"CLa8vteVgvPM2wEQw8mfzZCWigMYrdHBoZ7_igM%3D\",\"userInterfaceTheme\":\"USER_INTERFACE_THEME_DARK\",\"screenWidthPoints\":1470,\"screenHeightPoints\":474,\"screenPixelDensity\":2,\"screenDensityFloat\":2},\"request\":{\"returnLogEntry\":true,\"internalExperimentFlags\":[],\"eats\":\"Ac1K1YyqRgpIwfyBrUqDTmCFarp3+10mrRbvwMp7mb9Cc+tShOEfV4MfxTDf6hfPD+ZixjGFdcXS6pynPkCyO+ywSF0cWMtzSBCWMyg=\",\"sessionInfo\":{\"token\":\"YR1SZJKFZR\"},\"consistencyTokenJars\":[]},\"user\":{\"onBehalfOfUser\":\"108940515231048981095\",\"delegationContext\":{\"externalChannelId\":\"UCHPoNHk_aC5LmJDDVAH4w7Q\",\"roleType\":{\"channelRoleType\":\"CREATOR_CHANNEL_ROLE_TYPE_OWNER\"}},\"serializedDelegationContext\":\"EhhVQ0hQb05Ia19hQzVMbUpERFZBSDR3N1EqAggI\"},\"clientScreenNonce\":\"PIdrdlQgDFFE02Vs\"},\"trackingLabel\":\"web_explore_video\"}"
join_body = json.loads(join_body_str)

analytics_time_period_by_days = {
    7: "ANALYTICS_TIME_PERIOD_TYPE_WEEK",
    28: "ANALYTICS_TIME_PERIOD_TYPE_FOUR_WEEKS",
    90: "ANALYTICS_TIME_PERIOD_TYPE_QUARTER",
    365: "ANALYTICS_TIME_PERIOD_TYPE_YEAR",
    -1: "ANALYTICS_TIME_PERIOD_TYPE_SINCE_PUBLISH",
}


class Tab:
    def __init__(self, tab_Json: Json):
        self.tab_Json = tab_Json
        self.cards = self.tab_Json.cards
        self.key_metric_card_data = self.get_card("keyMetricCardData")["keyMetricCardData"]
        self.key_metric_tabs = self.key_metric_card_data["keyMetricTabs"]

    def get_card(self, cardName: str) -> Json:
        for card in self.cards:
            if cardName in card:
                return card
        raise Exception(f"card {cardName} not found")

    def get_metrics(self) -> list[str]:
        metrics = []
        for keyTab in self.key_metric_tabs:
            metric = keyTab["metricTabConfig"]["metric"].unwrap_str()
            metrics.append(metric)
        return metrics

    def get_metric_tab(self, metric_tab_name: str) -> Json:
        for keyTab in self.key_metric_tabs:
            if keyTab["metricTabConfig"]["metric"].unwrap_str() == metric_tab_name:
                return keyTab
        raise Exception(f"metric tab {metric_tab_name} not found")

    def get_series(self, metric_name: str) -> list[tuple[datetime.datetime, float]]:
        metricTab = self.get_metric_tab(metric_name)
        primaryContent = metricTab["primaryContent"]
        # print('preimaryContent metric', primaryContent["metric"].unwrap_str())
        # print(primaryContent["metric"])
        series = cast(list[dict[str, Any]], primaryContent["mainSeries"]["datums"].data)
        # return series
        xy = [(pt["x"], pt["y"]) for pt in series]
        xy = [(datetime.datetime.fromtimestamp(x / 1000), y) for x, y in xy]
        return xy

    def get_metric_total_from_key_metric_tabs(self, metric_name: str) -> int | float:
        metric_tab = self.get_metric_tab(metric_tab_name=metric_name)
        total = metric_tab["primaryContent"]["total"].unwrap_int()
        return total

    def get_metric_total_from_tab(self, metric_name: str):
        v = self.get_metric_total_from_key_metric_tabs(metric_name)
        return v

    def get_float_metric_total_from_tab(self, metric_name: str) -> float:
        v = self.get_metric_total_from_tab(metric_name=metric_name)
        v = cast(float, v)
        return v

    def get_int_metric_total_from_tab(self, metric_name: str) -> int:
        v = self.get_metric_total_from_tab(metric_name=metric_name)
        v = cast(int, v)
        return v


class StudioScraper:
    def __init__(self, get_screen_js_filepath: str) -> None:
        with open(get_screen_js_filepath) as f:
            self.query_raw = f.read()
        self.query_json = self.query_raw.partition(", ")[2].rstrip()[:-2]
        self.query = json.loads(self.query_json)
        self.headers = self.query["headers"]
        self.body_str = self.query["body"]
        self.body = json.loads(self.body_str)
        self.url = self.query_raw.partition(",")[0].split('"')[1]

    def get_likes_dislikes(self, video_id: str, days: int) -> tuple[int, int]:
        join_body_rendered = self._render_join_body(join_body, video_id=video_id, days=days)

        join_res = requests.post(join_url, headers=self.headers, data=json.dumps(join_body_rendered))
        if join_res.status_code >= 300:
            raise Exception("failed", join_res.status_code, join_res.content)
        join_json = join_res.json()
        results = join_json["results"]
        totals = self._get_join_result(results, "0__TOTALS_SUMS_QUERY_KEY")
        metric_columns = totals["value"]["resultTable"]["metricColumns"]
        likes = metric_columns[1]["counts"].get("total", 0)
        dislikes = metric_columns[2]["counts"].get("total", 0)
        return likes, dislikes

    def load_tab(self, tab_name: str, video_id: str, days: int) -> Tab:
        screen_config = self.body["screenConfig"]
        screen_config["entity"]["videoId"] = video_id
        screen_config["timePeriod"]["timePeriodType"] = analytics_time_period_by_days[days]
        desktop_state = self.body["desktopState"]
        desktop_state["tabId"] = tab_name
        body_str = json.dumps(self.body)
        res = requests.post(self.url, headers=self.headers, data=body_str)
        if res.status_code >= 300:
            raise Exception('ERROR', res, res.json())
        return Tab(Json(res.json()))

    def _get_join_result(self, join_json_results, join_key: str):
        for r in join_json_results:
            if r["key"] == join_key:
                return r
        raise Exception(f"Could not find join result {join_key}")

    def _render_join_body(self, join_body, video_id: str, days: int):
        for node in join_body["nodes"]:
            restricts = node["value"]["query"]["restricts"]
            restricts[0]["inValues"][0] = video_id
            date_id_range = node["value"]["query"]["timeRange"]["dateIdRange"]
            end_str = datetime.date.today().strftime("%Y%m%d")
            start_str = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y%m%d")
            date_id_range["inclusiveStart"] = start_str
            date_id_range["exclusiveEnd"] = end_str
        return join_body
