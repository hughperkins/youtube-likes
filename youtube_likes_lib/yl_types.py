from dataclasses import dataclass, field
from typing import Any

from youtube_likes_lib import process_logs


@dataclass
class Channel:
    name: str
    id: str
    abbrev: str
    log_videos: list[str] = field(default_factory=list)
    stats_baselines: dict[str, Any] = field(default_factory=dict)
    specific_videos: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Config:
    api_key: str
    min_change_interval_minutes: int
    send_smtp: bool
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_to_email: str
    smtp_subject: str
    channels: list[Channel]

    cache_file_path_templ: str
    reporting_job_id: str

    google_client_id: str
    google_client_secret: str
    google_refresh_token: str

    views_log_filepath_templ: str
    views_by_video_log_filepath_templ: str


@dataclass
class Video:
    video_id: str
    title: str
    likes: int = 0
    comments: int = 0
    views: int = 0


@dataclass
class StatsSnapshot:
    num_subscriptions: int
    videos: list[Video]
    total_views: int
    total_likes: int
    delta_by_time: dict[int, process_logs.DeltaStats]


@dataclass
class Output:
    is_priority: bool = False
    priority_reasons_title: str = ""
    priority_reasons_desc: str = ""
    body: str = ""
    email_message: str = ""
