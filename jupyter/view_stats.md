---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
# ignore this cell. go to next cell...
# download the following file from creator studio "Video Analytics" page, for a specific video
# by going into dev console, network, reloading the "Video Analytics" page, for a specific video
# and filtering on 'card'
# select, copy the 'response' from 'get_cards' call
# paste into a file, and edit get_cards_output_filepath, to point to that file

get_cards_output_filepath = '/tmp/get_cards.json'

# do the same thing but for 'join' search eam
join_output_filepath = '/tmp/join2.json'

import json

# first examine get_cards:

if True:
    with open(get_cards_output_filepath) as f:
        d = json.load(f)
    
    cards = d['cards']
    print(len(cards))
    for card in cards:
        print('card ==============')
        # print(card)
        print(card.keys())
        for to_print in ['personalizedHeaderCardData', 'config', 'isHidden']:
            if to_print in card:
                print(to_print, card[to_print])
        # for k in card.keys():
        #     if k.endswith('CardData'):
        #         print(k, card[k])
        # print(card['personalizedHeaderCardData'])

    card = cards[0]

    print('card.keys()', card.keys())
    
    # latestActivityCardData is the views in the last 48 hours and last hour
    datas = card["latestActivityCardData"]["datas"]
    print('len(datas)', len(datas))
    for data in datas:
        print(data["timePeriod"])
        mainChartData = data["mainChartData"]
        
                
# # now examine 'join'

# with open(join_output_filepath) as f:
#     d = json.load(f)
# results = d['results']
# for result in results:
#     # print(result.keys())
#     print(result['key'])
```

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
    x, y = list(zip(*xy))
    plt.plot(x, y)
    plt.title(primaryContent["metric"])
    plt.show()

max_days_old = 21

plot_graph('VIEWS', max_days_old)

plot_graph('WATCH_TIME', max_days_old)

plot_graph('SUBSCRIBERS_NET_CHANGE', max_days_old)

```

```python
%matplotlib inline
# download the following file from creator studio "Video Analytics" page, for a specific video
# by going into dev console, network, reloading the "Video Analytics" page, for a specific video,
# in the "reach" tab
# and filtering on 'screen'
# select, copy the 'response' from 'get_screen' call
# paste into a file, and edit get_screen_reach_filepath, to point to that file

import matplotlib.pyplot as plt
import datetime

get_screen_reach_filepath = '/tmp/get_screen_reach.json'

import json

with open(get_screen_reach_filepath) as f:
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
    x, y = list(zip(*xy))
    plt.plot(x, y)
    plt.title(primaryContent["metric"])
    plt.show()

max_days_old = 3

plot_graph('VIDEO_THUMBNAIL_IMPRESSIONS', max_days_old)

plot_graph('VIDEO_THUMBNAIL_IMPRESSIONS_VTR', max_days_old)

# plot_graph('VIEWS', max_days_old)

```
