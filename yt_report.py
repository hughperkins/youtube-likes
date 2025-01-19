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
from typing import Optional

import chili

import youtube_likes as yl
from youtube_likes_lib import studio_scraping


@dataclass
class ReportLine:
    title: str
    video_id: str
    views: int
    likes: int
    likes_per_k: int
    dislikes_per_k: int
    ctr: float


def get_video_stats(get_screen_js: str, video_id: str, title: str, days: int) -> Optional[ReportLine]:
    studio_scraper = studio_scraping.StudioScraper(get_screen_js_filepath=get_screen_js)

    likes, dislikes = studio_scraper.get_likes_dislikes(video_id=video_id, days=days)

    reach_tab = studio_scraper.load_tab(tab_name="ANALYTICS_TAB_ID_REACH", video_id=video_id, days=days)
    metrics = studio_scraper.get_metrics(reach_tab)
    if 'SHORTS_FEED_IMPRESSIONS' in metrics:
        print('short => skipping')
        return None

    engagement_tab = studio_scraper.load_tab(tab_name="ANALYTICS_TAB_ID_ENGAGEMENT", video_id=video_id, days=days)

    impressions = studio_scraper.get_int_metric_total_from_tab(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS")
    ctr = studio_scraper.get_float_metric_total_from_tab(reach_tab, "VIDEO_THUMBNAIL_IMPRESSIONS_VTR")
    views = studio_scraper.get_int_metric_total_from_tab(reach_tab, "VIEWS")

    average_watch_time_ms = studio_scraper.get_metric_total_from_tab(engagement_tab, "AVERAGE_WATCH_TIME")
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
    parser.add_argument('--days', default=28, type=int, choices=studio_scraping.analytics_time_period_by_days.keys())
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
