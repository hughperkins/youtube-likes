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

# to get the following file, go to studio analytics page for channel,
# tab 'overview', open the dev panel, with 'network'
# refresh page
# filter on 'scr', copy get_screen

from typing import Tuple
import matplotlib.pyplot as plt
from os.path import expanduser as expand
import datetime
import json

overview_file = expand('/tmp/channel_overview.json')

with open(overview_file) as f:
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

def get_data(metric_name, max_days_old, aggreg_over, scale_values: float = 1):
    metricTab = get_metric_tab(keyMetricTabs, metric_name)
    primaryContent = metricTab["primaryContent"]
    # print(primaryContent["metric"])
    series = primaryContent["mainSeries"]["datums"]
    
    xy = [(pt["x"], pt["y"]) for pt in series]
    xy = [(datetime.datetime.fromtimestamp(x / 1000), y) for x, y in xy]
    xy = [(- (datetime.datetime.now() - x).total_seconds() / 3600 / 24, y) for x, y in xy if (datetime.datetime.now() - x).total_seconds() / 3600 / 24 <= max_days_old]
    xy = [(x, y) for x, y in xy if x >= - max_days_old]
    xy = [(x, y * scale_values) for x, y in xy]
    deltas = []
    # last_x, last_y = None, None
    for n, (x, y) in enumerate(xy):
        # if last_x is not None:
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
    

def plot_graph(metric_name, max_days_old, aggreg_over: int = 1, scale_values: float = 1):
    metricTab = get_metric_tab(keyMetricTabs, metric_name)
    primaryContent = metricTab["primaryContent"]
    # print(primaryContent["metric"])
    series = primaryContent["mainSeries"]["datums"]
    
    xy = [(pt["x"], pt["y"]) for pt in series]
    xy = [(datetime.datetime.fromtimestamp(x / 1000), y) for x, y in xy]
    xy = [(- (datetime.datetime.now() - x).total_seconds() / 3600 / 24, y) for x, y in xy if (datetime.datetime.now() - x).total_seconds() / 3600 / 24 <= max_days_old]
    xy = [(x, y) for x, y in xy if x >= - max_days_old]
    xy = [(x, y * scale_values) for x, y in xy]
    deltas = []
    # last_x, last_y = None, None
    for n, (x, y) in enumerate(xy):
        # if last_x is not None:
        if aggreg_over >= 1:
            if n >= aggreg_over:
                y_avg = (y - xy[n - aggreg_over][1]) / aggreg_over
                deltas.append((x, y_avg))
        else:
            deltas.append((x, y))
        # last_x, last_y = x, y
    xy = deltas
    x, y = list(zip(*xy))
    plt.plot(x, y)
    title = primaryContent["metric"]
    if aggreg_over >= 1:
        title += ' delta'
    plt.title(title)
    if aggreg_over >= 1:
        plt.ylim([0, max(y)])
    plt.show()

def plot_graph2(title: str, xy_l, y_from_zero: bool = False, log_y: bool = False):
    x, y = xy_l
    plt.plot(x, y)
    plt.title(title)
    if y_from_zero:
        plt.ylim([0, max(y)])
    if log_y:
        plt.yscale('log')
    plt.show()

def cumul(xy_l: Tuple[list[float], list[float]]) -> Tuple[list[float], list[float]]:
    # xy_cumul = []
    y_sofar = 0
    x_l, y_l = xy_l
    y_cumul = []
    for x, y in zip(*(x_l, y_l)):
        y_sofar += y
        y_cumul.append(y_sofar)
    return x_l, y_cumul

max_days_old = 1000
watch_time_agg = 1

watch_time_cumul = get_data('WATCH_TIME', max_days_old, -1, scale_values=1/3600/1000)
# watch_time_delta = get_data('WATCH_TIME', max_days_old, watch_time_agg, scale_values=1/3600/1000)
watch_time_delta = get_data('WATCH_TIME', max_days_old, 1, scale_values=1/3600/1000)

# print(watch_time)

plot_graph2('watch time cumul (hours)', watch_time_cumul)
plot_graph2('watch time cumul (hours)', watch_time_cumul, log_y=True)

plot_graph2('watch time delta (hours)', watch_time_delta)
plot_graph2('watch time delta (hours)', watch_time_delta, log_y=True)

# watch_time_cumul = cumul(watch_time_delta)

# plot_graph2('watch time cumul (hours)', watch_time_cumul)
# plot_graph2('watch time cumul (hours)', watch_time_cumul, log_y=True)

# plot_graph('WATCH_TIME', max_days_old, -1, scale_values=1/3600/1000)
# plot_graph('WATCH_TIME', max_days_old, watch_time_agg, scale_values=1/3600)

```
