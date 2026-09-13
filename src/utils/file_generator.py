"""Render analysed reviews into a downloadable text report."""

from datetime import datetime, timezone
from typing import List, Optional

SEPARATOR = "-" * 60


def build_report(
    reviews: List[str],
    sentiments: List[str],
    scores: List[float],
    replies: List[str],
    sentiment_methods: Optional[List[str]] = None,
    reply_methods: Optional[List[str]] = None,
) -> str:
    """Build the report as a string.

    Kept in memory rather than written to disk: the previous version wrote a
    timestamped file under downloads/ and read it straight back, which on a
    hosted deploy just accumulates files on an ephemeral disk.

    sentiment_methods and reply_methods are labelled on their own lines so the
    reader can tell which engine produced each half of the output.
    """
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"App Review Assistant report - generated {generated}", "", SEPARATOR, ""]

    blank = [""] * len(reviews)
    sentiment_methods = sentiment_methods or blank
    reply_methods = reply_methods or blank

    records = zip(reviews, sentiments, scores, replies, sentiment_methods, reply_methods)

    for i, (review, sentiment, score, reply, s_method, r_method) in enumerate(
        records, start=1
    ):
        lines.append(f"Review {i}:")
        lines.append(review)
        lines.append("")

        s_engine = f", engine={s_method}" if s_method else ""
        lines.append(f"Sentiment: {sentiment} (score={score:.3f}{s_engine})")
        lines.append("")

        r_engine = f" (engine={r_method})" if r_method else ""
        lines.append(f"Reply{r_engine}:")
        lines.append(reply)
        lines.append("")
        lines.append(SEPARATOR)
        lines.append("")

    return "\n".join(lines)


def build_report_filename(label: str = "app_reviews") -> str:
    """Timestamped download filename, e.g. app_reviews_reviews_20260911_101500.txt."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = "".join(c for c in label if c.isalnum() or c in ("-", "_")) or "app"
    return f"{safe}_reviews_{timestamp}.txt"
