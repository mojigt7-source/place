from __future__ import annotations

import math
from datetime import datetime
from typing import Dict

from .models import Post


CONTENT_WEIGHTS: Dict[str, float] = {
    "reel": 1.2,
    "carousel": 1.1,
    "photo": 1.0,
    "image": 1.0,
    "video": 1.05,
}


def base_engagement(post: Post) -> int:
    return post.likes + 2 * post.comments + 3 * (post.shares + post.saves)


def engagement_rate(post: Post) -> float:
    if post.followers <= 0:
        return 0.0
    return base_engagement(post) / float(post.followers)


def recency_weight(post: Post, now: datetime | None = None, half_life_days: float = 7.0) -> float:
    now = now or datetime.now()
    age_days = max(0.0, (now - post.timestamp).total_seconds() / 86400.0)
    if half_life_days <= 0:
        return 1.0
    lam = math.log(2) / half_life_days
    return math.exp(-lam * age_days)


def content_type_weight(post: Post) -> float:
    return CONTENT_WEIGHTS.get(post.content_type.lower(), 1.0)


def caption_weight(post: Post, optimal_min: int = 100, optimal_max: int = 200) -> float:
    length = len(post.caption or "")
    if length <= 0:
        return 0.9
    if optimal_min <= length <= optimal_max:
        return 1.05
    # soft penalty for too short/too long
    if length < optimal_min:
        # linear from 0.9 (0 chars) to 1.05 (optimal_min)
        return 0.9 + (1.05 - 0.9) * (length / max(1, optimal_min))
    else:
        # decay as it gets longer beyond optimal_max
        over = length - optimal_max
        return max(0.9, 1.05 * math.exp(-over / 200.0))


def hashtags_weight(post: Post, optimal_min: int = 3, optimal_max: int = 5) -> float:
    count = max(0, int(post.hashtags_count))
    if count == 0:
        return 0.92
    if optimal_min <= count <= optimal_max:
        return 1.04
    if count > 15:
        return 0.9
    # mild penalty for too many or too few
    if count < optimal_min:
        # linear from 0.92 (0) to 1.04 (optimal_min)
        return 0.92 + (1.04 - 0.92) * (count / max(1, optimal_min))
    else:
        # decay as count increases beyond optimal_max up to 0.9
        over = count - optimal_max
        return max(0.9, 1.04 * math.exp(-over / 6.0))


def post_score(post: Post, now: datetime | None = None) -> float:
    er = engagement_rate(post)
    r = recency_weight(post, now=now)
    ctw = content_type_weight(post)
    cw = caption_weight(post)
    hw = hashtags_weight(post)
    return er * r * ctw * cw * hw
