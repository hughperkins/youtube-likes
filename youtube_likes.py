# Note, if you run this from crontab, you should put the following in front
# of the python command:
# PYTHONIOENCODING=utf-8
# eg
# PYTHONIOENCODING=utf-8 python youtube_likes.py
# (otherwise it won't handle non-latin characters ok)

import requests
import argparse
import json
from os import path
from ruamel import yaml

import warnings
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)


def run(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f)
    # print('config', config)

    api_key = config['api_key']
    channel_id = config['channel_id']

    persisted = {}

    res = requests.get('https://www.googleapis.com/youtube/v3/channels/?id={channel_id}'
                       '&part=statistics'
                       '&key={api_key}'.format(
                            channel_id=channel_id,
                            api_key=api_key))
    if res.status_code != 200:
        print('res.status_code %s' % res.status_code)
        print(res.content)
        raise Exception('invalid status code %s' % res.status_code)
    d = json.loads(res.content.decode('utf-8'))
    # print(json.dumps(d, indent=2))
    persisted['num_subscriptions'] = d['items'][0]['statistics']['subscriberCount']
    # print('num_subscriptions %s')
    res = requests.get(
        'https://www.googleapis.com/youtube/v3/activities/?maxResults=25'
        '&channelId={channel_id}'
        '&part=snippet%2CcontentDetails'
        '&key={api_key}'.format(api_key=api_key, channel_id=channel_id))
    if res.status_code != 200:
        print('res.status_code %s' % res.status_code)
        print(res.content)
    assert res.status_code == 200
    d = json.loads(res.content.decode('utf-8'))
    videos = []
    for item in d['items']:
        title = item['snippet']['title']
        video_id = item['contentDetails']['upload']['videoId']
        videos.append({'title': title, 'video_id': video_id})

    res = requests.get('https://www.googleapis.com/youtube/v3/videos/?id={video_ids}'
                       '&part=snippet%2CcontentDetails%2Cstatistics'
                       '&key={api_key}'.format(
                            video_ids=','.join([v['video_id'] for v in videos]),
                            api_key=api_key))
    assert res.status_code == 200
    d = json.loads(res.content.decode('utf-8'))
    videos = []
    persisted['videos'] = videos
    for item in d['items']:
        video_id = item['id']
        title = item['snippet']['title']
        s = item['statistics']
        likes = s['likeCount']
        views = s['viewCount']
        favorites = s['favoriteCount']
        comments = s['commentCount']
        videos.append({
            'video_id': video_id,
            'title': title,
            'likes': likes,
            'views': views,
            'favorites': favorites,
            'comments': comments
            })
    # print(yaml.dump(videos))
    # print(json.dumps(videos, indent=2))
    # print(json.dumps(videos, indent=2))
    if path.isfile(config['cache_file']):
        with open(config['cache_file'], 'r') as f:
            old_persisted = yaml.load(f)
            if 'videos' not in old_persisted:
                old_persisted = {
                    'videos': old_persisted,
                    'num_subscriptions': 0
                }
    else:
        # old_stats = []
        old_persisted = {'videos': [], 'num_subscriptions': 0}
    old_videos = old_persisted['videos']
    old_by_id = {}
    for video in old_videos:
        old_by_id[video['video_id']] = video
    new_by_id = {}
    for video in videos:
        new_by_id[video['video_id']] = video
    for video_id, video in new_by_id.items():
        if video_id not in old_by_id:
            print('new:')
            print(json.dumps(video, indent=2))
        else:
            old_video = old_by_id[video_id]
            # if json.dumps(old_video) != json.dumps(video):
                # print(json.dumps(sorted(old_video.items())))
                # print(json.dumps(sorted(video.items())))
            output = ''
            for k in video.keys():
                if k == 'video_id':
                    continue
                if old_video[k] != video[k]:
                    output += '  %s %s => %s\n' % (k, old_video[k], video[k])
            if output != '':
                print((video['title'] + ':'))
                print(output[:-1])

    if persisted['num_subscriptions'] != old_persisted['num_subscriptions']:
        print('num subscriptions: %s => %s' % (
            old_persisted['num_subscriptions'], persisted['num_subscriptions']))

    with open(config['cache_file'], 'w') as f:
        yaml.dump(persisted, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.yml', type=str)
    args = parser.parse_args()
    run(**args.__dict__)
