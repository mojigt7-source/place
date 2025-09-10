from __future__ import annotations

import argparse
import os
from datetime import datetime

from .analysis import load_posts, summarize_accounts
from .report import generate_markdown_report


def analyze(input_path: str, output_path: str | None) -> int:
    posts = load_posts(input_path)
    # برای جلوگیری از صفر شدن وزن تازگی در دیتاست‌های قدیمی، اکنون را جدیدترین زمان پست در نظر می‌گیریم
    now_ref = max((p.timestamp for p in posts), default=datetime.now())
    summaries = summarize_accounts(posts, now=now_ref)
    report_md = generate_markdown_report(summaries)

    if output_path:
        out_dir = os.path.dirname(output_path) or "."
        os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"گزارش ساخته شد: {output_path}")
    else:
        print(report_md)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ig_competitor_analysis",
        description="تحلیل رقبا و امتیازدهی محتوا بر اساس الگوریتم اینستاگرام (تقریبی)",
    )
    parser.add_argument(
        "--input",
        dest="input",
        required=True,
        help="مسیر فایل CSV ورودی",
    )
    parser.add_argument(
        "--output",
        dest="output",
        required=False,
        default=None,
        help="مسیر خروجی گزارش Markdown (مثلاً reports/report.md). اگر نگذارید، در ترمینال چاپ می‌شود.",
    )

    args = parser.parse_args(argv)
    return analyze(args.input, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
