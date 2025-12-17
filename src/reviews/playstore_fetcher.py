
from typing import List
from google_play_scraper import reviews, Sort

def fetch_playstore_reviews(app_id: str, limit: int = 20, lang: str = "en", country: str = "in") -> List[str]:
    """Fetch recent reviews for a Google Play app using its package name.

    app_id: e.g., 'com.whatsapp'
    limit: number of reviews to fetch (best-effort)
    lang: language code, e.g. 'en'
    country: country code, e.g. 'in'
    """
    if not app_id:
        return []

    result, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=limit
    )

    texts = [r.get("content", "").strip() for r in result if r.get("content")]
    return texts
