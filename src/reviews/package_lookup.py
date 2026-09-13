"""Resolve a human app name (e.g. "Netflix") to a Play Store package id.

Primary strategy is parsing the Play Store search page, which reliably yields
the true top result. google_play_scraper.search() is only a fallback: in
google-play-scraper 1.2.7 its first (best) hit returns appId=None, so taking
hit[0] would break and hit[1] is a different app (searching "Netflix" gives
com.netflix.ninja, not com.netflix.mediaclient).
"""

import logging
import re
import urllib.parse
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

SEARCH_URL = "https://play.google.com/store/search"
TIMEOUT = 10

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Reverse-domain package ids, e.g. com.netflix.mediaclient, notion.id
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")


def _is_valid_package(package_id: str) -> bool:
    return bool(package_id) and bool(PACKAGE_RE.match(package_id))


def _extract_package_ids(html: str) -> List[str]:
    """Pull app package ids out of a Play Store search page, in page order.

    Parses the href query string properly rather than scanning for "id=",
    which would also match inside other parameters.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: List[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/store/apps/details" not in href:
            continue

        query = urllib.parse.urlparse(href).query
        package_id = urllib.parse.parse_qs(query).get("id", [""])[0]

        if _is_valid_package(package_id) and package_id not in found:
            found.append(package_id)

    return found


def _best_match(candidates: List[str], app_name: str) -> Optional[str]:
    """Pick the most plausible candidate for app_name.

    The first link on the page is usually the top result, but it can be a
    promoted or related app. So if any candidate's package id contains a word
    from the query, prefer it. Otherwise keep page order. This is a preference,
    not a filter: plenty of real apps have unrelated package ids (Threads is
    com.instagram.barcelona).
    """
    if not candidates:
        return None

    tokens = [t for t in re.split(r"[^a-z0-9]+", app_name.lower()) if len(t) > 2]
    for candidate in candidates:
        flat = candidate.lower().replace(".", "")
        if any(token in flat for token in tokens):
            return candidate

    return candidates[0]


def _search_fallback(app_name: str, lang: str, country: str) -> Optional[str]:
    """Fallback via google_play_scraper, skipping hits with no appId."""
    try:
        from google_play_scraper import search
    except ImportError:
        return None

    try:
        hits = search(app_name, lang=lang, country=country, n_hits=5)
    except Exception as exc:
        log.warning("google_play_scraper search failed: %s", exc)
        return None

    usable = [h.get("appId") for h in hits if _is_valid_package(h.get("appId") or "")]
    if not usable:
        log.warning("search() returned no usable appId for %r", app_name)
        return None

    return _best_match(usable, app_name)


def get_package_from_app_name(
    app_name: str, lang: str = "en", country: str = "in"
) -> Optional[str]:
    """Return the package id for app_name, or None if it cannot be resolved."""
    app_name = (app_name or "").strip()
    if not app_name:
        return None

    params = {"c": "apps", "q": app_name, "hl": lang, "gl": country}
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        candidates = _extract_package_ids(resp.text)
        match = _best_match(candidates, app_name)
        if match:
            log.info("Resolved %r to %s", app_name, match)
            return match
        log.info("No app link on search page for %r; trying search()", app_name)

    except requests.RequestException as exc:
        log.warning("Play Store search request failed (%s); trying search()", exc)
    except Exception as exc:
        log.warning("Play Store search parse failed (%s); trying search()", exc)

    return _search_fallback(app_name, lang, country)
