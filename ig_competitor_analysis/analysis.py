from __future__ import annotations

import csv
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime
from statistics import median
from typing import List, Dict, Iterable, Tuple

from .models import Post
from .algo import post_score, engagement_rate, base_engagement


@dataclass
class PostWithScore:
    post: Post
    score: float


@dataclass
class AccountSummary:
    username: str
    posts_count: int
    posts_per_week: float
    avg_eng_rate_pct: float
    avg_post_score: float
    top_content_type: str
    best_hour_local: int | None
    top_posts: List[PostWithScore]


def load_posts(csv_path: str) -> List[Post]:
    posts: List[Post] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                posts.append(Post.from_row(row))
            except Exception:
                # skip invalid rows silently
                continue
    return posts


def group_by_user(posts: Iterable[Post]) -> Dict[str, List[Post]]:
    grouped: Dict[str, List[Post]] = defaultdict(list)
    for p in posts:
        grouped[p.username].append(p)
    return grouped


def compute_posts_per_week(posts: List[Post]) -> float:
    if not posts:
        return 0.0
    dates = sorted(p.timestamp for p in posts)
    span_days = max(1.0, (dates[-1] - dates[0]).total_seconds() / 86400.0)
    weeks = span_days / 7.0
    return len(posts) / weeks if weeks > 0 else float(len(posts))


def best_hour(posts_scored: List[PostWithScore]) -> int | None:
    if not posts_scored:
        return None
    # weighted by score for top 50% posts
    sorted_ps = sorted(posts_scored, key=lambda x: x.score, reverse=True)
    cutoff = max(1, len(sorted_ps) // 2)
    hours = []
    for pws in sorted_ps[:cutoff]:
        hours.append(pws.post.timestamp.hour)
    if not hours:
        return None
    try:
        return int(median(hours))
    except Exception:
        # fallback to most common
        return Counter(hours).most_common(1)[0][0]


def summarize_accounts(posts: List[Post], now: datetime | None = None, top_k_posts: int = 3) -> List[AccountSummary]:
    grouped = group_by_user(posts)
    summaries: List[AccountSummary] = []
    for user, user_posts in grouped.items():
        scored = [PostWithScore(p, post_score(p, now=now)) for p in user_posts]
        posts_per_week = compute_posts_per_week(user_posts)
        avg_er = 0.0
        if user_posts:
            avg_er = sum(engagement_rate(p) for p in user_posts) / len(user_posts)
        avg_score = 0.0
        if scored:
            avg_score = sum(x.score for x in scored) / len(scored)
        type_counter = Counter(p.content_type for p in user_posts)
        top_content_type = type_counter.most_common(1)[0][0] if type_counter else ""
        bh = best_hour(scored)
        top_posts = sorted(scored, key=lambda x: x.score, reverse=True)[:top_k_posts]
        summaries.append(
            AccountSummary(
                username=user,
                posts_count=len(user_posts),
                posts_per_week=posts_per_week,
                avg_eng_rate_pct=avg_er * 100.0,
                avg_post_score=avg_score,
                top_content_type=top_content_type,
                best_hour_local=bh,
                top_posts=top_posts,
            )
        )
    # sort by avg_post_score desc
    summaries.sort(key=lambda s: s.avg_post_score, reverse=True)
    return summaries
