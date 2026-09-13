"""Fetch review text for a Google Play app."""

import logging
from typing import List

from google_play_scraper import Sort, reviews

log = logging.getLogger(__name__)

MAX_COUNT = 200


def fetch_playstore_reviews(
    app_id: str, limit: int = 20, lang: str = "en", country: str = "in"
) -> List[str]:
    """Fetch the newest reviews for a Play Store app.

    app_id: package name, e.g. 'com.whatsapp'
    limit: how many reviews to fetch (best-effort, capped at MAX_COUNT)
    lang: language code, e.g. 'en'
    country: country code, e.g. 'in'

    Returns the non-empty review bodies. Note that the Play Store also exposes
    a star rating per review, which this project does not use yet.
    """
    if not app_id:
        return []

    count = max(1, min(int(limit), MAX_COUNT))

    result, _ = reviews(
        app_id,
        lang=lang or "en",
        country=country or "in",
        sort=Sort.NEWEST,
        count=count,
    )

    texts = [(r.get("content") or "").strip() for r in result]
    texts = [t for t in texts if t]

    log.info("Fetched %d usable reviews for %s", len(texts), app_id)
    return texts
