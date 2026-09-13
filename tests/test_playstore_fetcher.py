"""Tests for the review fetcher. No network required."""

from src.reviews import playstore_fetcher as pf


def _capture(monkeypatch, payload=None):
    """Patch the scraper and record the kwargs it was called with."""
    seen = {}

    def fake(app_id, **kwargs):
        seen.update(kwargs)
        seen["app_id"] = app_id
        return (payload or [], None)

    monkeypatch.setattr(pf, "reviews", fake)
    return seen


class TestFetchPlaystoreReviews:
    def test_blank_app_id_short_circuits(self):
        assert pf.fetch_playstore_reviews("") == []
        assert pf.fetch_playstore_reviews(None) == []

    def test_filters_empty_and_whitespace_content(self, monkeypatch):
        payload = [
            {"content": "Good app"},
            {"content": "   "},
            {"content": None},
            {},
            {"content": "  Bad app  "},
        ]
        _capture(monkeypatch, payload)
        assert pf.fetch_playstore_reviews("com.x") == ["Good app", "Bad app"]

    def test_caps_count_at_max(self, monkeypatch):
        seen = _capture(monkeypatch)
        pf.fetch_playstore_reviews("com.x", limit=10_000)
        assert seen["count"] == pf.MAX_COUNT

    def test_floors_count_at_one(self, monkeypatch):
        seen = _capture(monkeypatch)
        pf.fetch_playstore_reviews("com.x", limit=0)
        assert seen["count"] == 1

    def test_passes_through_normal_limit(self, monkeypatch):
        seen = _capture(monkeypatch)
        pf.fetch_playstore_reviews("com.x", limit=20)
        assert seen["count"] == 20

    def test_blank_lang_country_get_defaults(self, monkeypatch):
        seen = _capture(monkeypatch)
        pf.fetch_playstore_reviews("com.x", lang="", country="")
        assert seen["lang"] == "en"
        assert seen["country"] == "in"

    def test_forwards_app_id_and_locale(self, monkeypatch):
        seen = _capture(monkeypatch)
        pf.fetch_playstore_reviews("com.whatsapp", lang="hi", country="in")
        assert seen["app_id"] == "com.whatsapp"
        assert seen["lang"] == "hi"

    def test_empty_result_is_empty_list(self, monkeypatch):
        _capture(monkeypatch, [])
        assert pf.fetch_playstore_reviews("com.x") == []
