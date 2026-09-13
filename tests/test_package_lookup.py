"""Tests for app-name to package-id resolution. No network required."""

import pytest
import requests

from src.reviews import package_lookup as pl


class TestIsValidPackage:
    @pytest.mark.parametrize(
        "pkg", ["com.netflix.mediaclient", "notion.id", "com.whatsapp", "com.a_b.c2"]
    )
    def test_accepts_real_package_ids(self, pkg):
        assert pl._is_valid_package(pkg)

    @pytest.mark.parametrize("pkg", ["", "nodots", "9bad.start", ".leading", "a..b"])
    def test_rejects_malformed(self, pkg):
        assert not pl._is_valid_package(pkg)


class TestExtractPackageIds:
    def test_parses_query_string_properly(self):
        # Regression: the old code did href.find("id=") across the whole href,
        # so other params before id= produced a mis-sliced package.
        html = '<a href="/store/apps/details?hl=en&gl=IN&id=com.real.app">x</a>'
        assert pl._extract_package_ids(html) == ["com.real.app"]

    def test_preserves_page_order_and_dedupes(self):
        html = (
            '<a href="/store/apps/details?id=com.first">a</a>'
            '<a href="/store/apps/details?id=com.first">dup</a>'
            '<a href="/store/apps/details?id=com.second">b</a>'
        )
        assert pl._extract_package_ids(html) == ["com.first", "com.second"]

    def test_ignores_non_app_links(self):
        html = (
            '<a href="/store/movies/details?id=movie123">movie</a>'
            '<a href="/about">about</a>'
        )
        assert pl._extract_package_ids(html) == []

    def test_skips_malformed_ids(self):
        html = '<a href="/store/apps/details?id=notapackage">x</a>'
        assert pl._extract_package_ids(html) == []

    def test_empty_html(self):
        assert pl._extract_package_ids("") == []


class TestBestMatch:
    def test_prefers_candidate_matching_the_query(self):
        candidates = ["com.promoted.ad", "com.netflix.mediaclient"]
        assert pl._best_match(candidates, "Netflix") == "com.netflix.mediaclient"

    def test_falls_back_to_page_order_when_nothing_matches(self):
        # Threads really is com.instagram.barcelona, so a name filter would be wrong.
        candidates = ["com.instagram.barcelona", "com.other.app"]
        assert pl._best_match(candidates, "Threads") == "com.instagram.barcelona"

    def test_ignores_short_tokens(self):
        # "an" must not match inside unrelated ids.
        assert pl._best_match(["com.zzz.aaa", "com.app.one"], "an") == "com.zzz.aaa"

    def test_empty_candidates(self):
        assert pl._best_match([], "Netflix") is None


class TestGetPackageFromAppName:
    @pytest.mark.parametrize("name", ["", "   ", None])
    def test_blank_name_short_circuits(self, name):
        assert pl.get_package_from_app_name(name) is None

    def test_happy_path(self, monkeypatch):
        class Resp:
            text = '<a href="/store/apps/details?id=com.netflix.mediaclient">n</a>'

            def raise_for_status(self):
                pass

        monkeypatch.setattr(pl.requests, "get", lambda *a, **k: Resp())
        assert pl.get_package_from_app_name("Netflix") == "com.netflix.mediaclient"

    def test_network_error_tries_search_fallback(self, monkeypatch):
        def boom(*a, **k):
            raise requests.RequestException("offline")

        monkeypatch.setattr(pl.requests, "get", boom)
        monkeypatch.setattr(pl, "_search_fallback", lambda *a, **k: "com.fallback.app")
        assert pl.get_package_from_app_name("Netflix") == "com.fallback.app"

    def test_returns_none_when_everything_fails(self, monkeypatch):
        def boom(*a, **k):
            raise requests.RequestException("offline")

        monkeypatch.setattr(pl.requests, "get", boom)
        monkeypatch.setattr(pl, "_search_fallback", lambda *a, **k: None)
        assert pl.get_package_from_app_name("Nonsense") is None

    def test_no_results_falls_through_to_search(self, monkeypatch):
        class Resp:
            text = "<html>no apps here</html>"

            def raise_for_status(self):
                pass

        monkeypatch.setattr(pl.requests, "get", lambda *a, **k: Resp())
        monkeypatch.setattr(pl, "_search_fallback", lambda *a, **k: "com.from.search")
        assert pl.get_package_from_app_name("Netflix") == "com.from.search"


class TestSearchFallback:
    def test_skips_hits_with_null_appid(self, monkeypatch):
        # google-play-scraper 1.2.7 returns appId=None for the best hit, so the
        # fallback must never take hits[0] blindly.
        import google_play_scraper

        hits = [
            {"appId": None, "title": "Netflix"},
            {"appId": "com.netflix.mediaclient", "title": "Netflix"},
        ]
        monkeypatch.setattr(google_play_scraper, "search", lambda *a, **k: hits)
        assert pl._search_fallback("Netflix", "en", "in") == "com.netflix.mediaclient"

    def test_all_null_returns_none(self, monkeypatch):
        import google_play_scraper

        monkeypatch.setattr(
            google_play_scraper, "search", lambda *a, **k: [{"appId": None}]
        )
        assert pl._search_fallback("Netflix", "en", "in") is None

    def test_search_exception_is_swallowed(self, monkeypatch):
        import google_play_scraper

        def boom(*a, **k):
            raise TypeError("'NoneType' object is not subscriptable")

        monkeypatch.setattr(google_play_scraper, "search", boom)
        assert pl._search_fallback("zzzz", "en", "in") is None
