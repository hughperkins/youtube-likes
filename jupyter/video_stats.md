---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
%matplotlib inline
# download the following file from creator studio "Video Analytics" page, for a specific video
# by going into dev console, network, reloading the "Video Analytics" page, for a specific video,
# in the "overview" tab
# and filtering on 'screen'
# select, copy the 'response' from 'get_screen' call
# paste into a file, and edit get_screen_output_filepath, to point to that file

import matplotlib.pyplot as plt
import datetime

get_screen_output_filepath = '/tmp/get_screen.json'

import json

with open(get_screen_output_filepath) as f:
    d = json.load(f)
cards = d["cards"]

def get_card(cards, cardName):
    for card in cards:
        if cardName in card:
            return card
    return None

def get_metric_tab(keyMetricTabs, tabName):
    for keyTab in keyMetricTabs:
        if keyTab["metricTabConfig"]["metric"] == tabName:
            return keyTab
    return None

for card in cards:
    if "personalizedHeaderCardData" in card:
        print(card["personalizedHeaderCardData"])

keyMetricCardData = get_card(cards, "keyMetricCardData")["keyMetricCardData"]
keyMetricTabs = keyMetricCardData["keyMetricTabs"]
for keyTab in keyMetricTabs:
    print(keyTab["metricTabConfig"])

def plot_graph(metric_name, max_days_old):
    metricTab = get_metric_tab(keyMetricTabs, metric_name)
    primaryContent = metricTab["primaryContent"]
    print(primaryContent["metric"])
    series = primaryContent["mainSeries"]["datums"]
    
    xy = [(pt["x"], pt["y"]) for pt in series]
    xy = [(datetime.datetime.fromtimestamp(x / 1000), y) for x, y in xy]
    xy = [(- (datetime.datetime.now() - x).total_seconds() / 3600 / 24, y) for x, y in xy if (datetime.datetime.now() - x).total_seconds() / 3600 / 24 <= max_days_old]
    xy = [(x, y) for x, y in xy if x >= - max_days_old]

    # deltas = []
    # last_x, last_y = None, None
    # for x, y in xy:
    #     if last_x is not None:
    #         deltas.append((x, y - last_y))
    #     last_x, last_y = x, y
    # xy = deltas

    x, y = list(zip(*xy))
    plt.plot(x, y)
    plt.title(primaryContent["metric"])
    plt.show()

max_days_old = 7

plot_graph('VIEWS', max_days_old)

plot_graph('WATCH_TIME', max_days_old)

plot_graph('SUBSCRIBERS_NET_CHANGE', max_days_old)

```

```python
%matplotlib inline
# download the following file from creator studio "Video Analytics" page, for a specific video
# by going into dev console, network, reloading the "Video Analytics" page, for a specific video,
# cahnge to '28 days'
# in the "reach" tab
# and filtering on 'screen'
# select, do 'copy' 'copy as fetch (js)'
# paste into a file, and edit get_screen_reach_js_filepath

import matplotlib.pyplot as plt
import datetime
import json
import sys
import importlib

sys.path.append('..')
from youtube_likes_lib import studio_scraping
importlib.reload(studio_scraping)

get_screen_reach_js_filepath = '/tmp/request.js'

videos = {
    '1J3awpFZwF4': 'trig mash 2',
    '_L0IYWUgkNo': '1000 miles',
    'eStB3qgWo1g': 'fonts v2',
    'NJ22jB_xOzA': 'ai takes jobs',
}

# video_id = '1J3awpFZwF4' # trigmash2
days = 7
max_days_old = 7

def get_data(xy, max_days_old, aggreg_over):
#     xy = reach.get_series(metric_name)
    
    xy = [(- (datetime.datetime.now() - x).total_seconds() / 3600 / 24, y) for x, y in xy if (datetime.datetime.now() - x).total_seconds() / 3600 / 24 <= max_days_old]
    xy = [(x, y) for x, y in xy if x >= - max_days_old]
    deltas = []
    for n, (x, y) in enumerate(xy):
        if aggreg_over >= 1:
            if n >= aggreg_over:
                y_avg = (y - xy[n - aggreg_over][1]) / aggreg_over
                deltas.append((x, y_avg))
        else:
            deltas.append((x, y))
        # last_x, last_y = x, y
    xy = deltas
    x, y = list(zip(*xy))
    return x, y
    

def plot_graph(ax, xy, metric_name, max_days_old, aggreg_over: int = 1, multiplier: float = 1):
#     xy = reach.get_series(metric_name)

    xy = [(- (datetime.datetime.now() - x).total_seconds() / 3600 / 24, y) for x, y in xy]
    xy = [(x, y) for x, y in xy if x >= - max_days_old]
    if multiplier != 1:
        xy = [(x, y * multiplier) for x, y in xy]
    deltas = []
    for n, (x, y) in enumerate(xy):
        if aggreg_over >= 1:
            if n >= aggreg_over:
                y_avg = (y - xy[n - aggreg_over][1]) / aggreg_over
                deltas.append((x, y_avg))
        else:
            deltas.append((x, y))
    xy = deltas
    x, y = list(zip(*xy))
#     plt.figure(figsize=(2, 2))
    ax.plot(x, y)
    title = metric_name
    if aggreg_over >= 1:
        title += ' delta'
    ax.set_title(title)
    if aggreg_over >= 1:
        ax.set_ylim([min(y), max(y)])
#     plt.show()

impressions_agg = 1
views_agg = 1
ctr_agg = 1

# impressions_agg = 16
# views_agg = 16
# ctr_agg = 16

for video_id, short_name in videos.items():
    print('=' * 80)
    print(short_name)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(8, 2))
    reach = studio_scraper.load_tab(tab_name="ANALYTICS_TAB_ID_REACH", video_id=video_id, days=days)
    engagement = studio_scraper.load_tab(tab_name="ANALYTICS_TAB_ID_ENGAGEMENT", video_id=video_id, days=days)

    plot_graph(ax1, reach.get_series('VIDEO_THUMBNAIL_IMPRESSIONS'), 'Impressions', max_days_old, 0)
    plot_graph(ax2, reach.get_series('VIEWS'), 'Views', max_days_old, 0)
    plot_graph(ax3, reach.get_series('VIDEO_THUMBNAIL_IMPRESSIONS_VTR'), 'Ctr', max_days_old, 0)
    plot_graph(ax4, engagement.get_series('AVERAGE_WATCH_TIME'), 'Avg watch time', max_days_old, 0, multiplier = 1 / 1000 / 60)
    plt.tight_layout()
    plt.show()

```
