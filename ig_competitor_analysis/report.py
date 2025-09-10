from __future__ import annotations

from datetime import datetime
from typing import List

from .analysis import AccountSummary, PostWithScore
from .algo import base_engagement, engagement_rate


def _format_time_hour(hour: int | None) -> str:
    if hour is None:
        return "نامشخص"
    # show as HH:00
    return f"{hour:02d}:00"


def _format_post_line(pws: PostWithScore, idx: int) -> str:
    p = pws.post
    er = engagement_rate(p) * 100.0
    return (
        f"{idx}. پست {p.post_id} | {p.timestamp.strftime('%Y-%m-%d %H:%M')} | "
        f"نوع: {p.content_type} | لایک: {p.likes}، کامنت: {p.comments}، ذخیره: {p.saves}، اشتراک: {p.shares} | "
        f"ER: {er:.2f}% | امتیاز: {pws.score:.6f}"
    )


def generate_markdown_report(summaries: List[AccountSummary], generated_at: datetime | None = None) -> str:
    generated_at = generated_at or datetime.now()
    lines: List[str] = []
    lines.append(f"# گزارش تحلیل رقبا (تولید: {generated_at.strftime('%Y-%m-%d %H:%M')})")
    lines.append("")
    if not summaries:
        lines.append("داده‌ای برای تحلیل وجود ندارد.")
        return "\n".join(lines)

    lines.append("## نمای کلی")
    for i, s in enumerate(summaries, start=1):
        lines.append(
            f"{i}. @{s.username} — پست‌ها: {s.posts_count} | پست/هفته: {s.posts_per_week:.2f} | "
            f"ER میانگین: {s.avg_eng_rate_pct:.2f}% | امتیاز میانگین: {s.avg_post_score:.6f} | "
            f"نوع برتر: {s.top_content_type} | بهترین ساعت: {_format_time_hour(s.best_hour_local)}"
        )

    lines.append("")
    lines.append("## جزئیات هر اکانت")

    for s in summaries:
        lines.append("")
        lines.append(f"### @{s.username}")
        lines.append(
            f"پست‌ها: {s.posts_count} | پست/هفته: {s.posts_per_week:.2f} | ER میانگین: {s.avg_eng_rate_pct:.2f}% | "
            f"امتیاز میانگین: {s.avg_post_score:.6f} | نوع محتوای غالب: {s.top_content_type} | "
            f"بهترین ساعت انتشار: {_format_time_hour(s.best_hour_local)}"
        )
        if not s.top_posts:
            lines.append("داده‌ای برای برترین پست‌ها موجود نیست.")
        else:
            lines.append("برترین پست‌ها:")
            for idx, pws in enumerate(s.top_posts, start=1):
                lines.append("- " + _format_post_line(pws, idx))

    return "\n".join(lines)
