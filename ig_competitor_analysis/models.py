from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


def _to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value).strip()
    if s == "":
        return default
    try:
        return int(float(s))
    except ValueError:
        return default


def _to_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _parse_ts(s: str) -> datetime:
    # Try common ISO formats
    s = s.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Fallback to fromisoformat if possible
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass
    raise ValueError(f"Unrecognized timestamp format: {s}")


@dataclass
class Post:
    username: str
    post_id: str
    timestamp: datetime
    content_type: str
    likes: int
    comments: int
    shares: int
    saves: int
    followers: int
    impressions: int
    reach: int
    video_views: int
    watch_time_seconds: int
    caption: str
    hashtags_count: int

    @staticmethod
    def from_row(row: Dict[str, Any]) -> "Post":
        username = _to_str(row.get("username"))
        post_id = _to_str(row.get("post_id"))
        ts_raw = _to_str(row.get("timestamp"))
        timestamp = _parse_ts(ts_raw)
        content_type = _to_str(row.get("content_type")).lower().strip() or "photo"
        likes = _to_int(row.get("likes"))
        comments = _to_int(row.get("comments"))
        shares = _to_int(row.get("shares"))
        saves = _to_int(row.get("saves"))
        followers = _to_int(row.get("followers"))
        impressions = _to_int(row.get("impressions"))
        reach = _to_int(row.get("reach"))
        video_views = _to_int(row.get("video_views"))
        watch_time_seconds = _to_int(row.get("watch_time_seconds"))
        caption = _to_str(row.get("caption"))

        hashtags_count = 0
        if "hashtags_count" in row and str(row.get("hashtags_count")).strip() != "":
            hashtags_count = _to_int(row.get("hashtags_count"))
        else:
            # rudimentary extraction from caption
            if caption:
                hashtags_count = caption.count("#")

        return Post(
            username=username,
            post_id=post_id,
            timestamp=timestamp,
            content_type=content_type,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=saves,
            followers=followers,
            impressions=impressions,
            reach=reach,
            video_views=video_views,
            watch_time_seconds=watch_time_seconds,
            caption=caption,
            hashtags_count=hashtags_count,
        )
