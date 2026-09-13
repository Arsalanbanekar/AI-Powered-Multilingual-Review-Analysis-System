"""Tests for the downloadable report."""

import re

import pytest

from src.utils.file_generator import build_report, build_report_filename

REVIEWS = ["Great app!", "Crashes on launch."]
SENTIMENTS = ["Positive", "Highly Negative"]
SCORES = [0.8, -0.9]
REPLIES = ["Thanks so much!", "Sorry about that."]
METHODS = ["groq", "template"]


class TestBuildReport:
    def test_includes_every_record(self):
        out = build_report(REVIEWS, SENTIMENTS, SCORES, REPLIES, METHODS)
        for text in REVIEWS + SENTIMENTS + REPLIES:
            assert text in out
        assert "Review 1:" in out and "Review 2:" in out

    def test_reports_engine_when_supplied(self):
        out = build_report(REVIEWS, SENTIMENTS, SCORES, REPLIES, METHODS)
        assert "engine=groq" in out
        assert "engine=template" in out

    def test_sentiment_and_reply_engines_are_not_confused(self):
        # Regression: both lines once showed the reply engine.
        out = build_report(
            ["r"], ["Positive"], [0.8], ["rep"],
            sentiment_methods=["groq"], reply_methods=["template"],
        )
        assert "Sentiment: Positive (score=0.800, engine=groq)" in out
        assert "Reply (engine=template):" in out

    def test_reply_engine_alone(self):
        out = build_report(
            ["r"], ["Positive"], [0.8], ["rep"], reply_methods=["groq"]
        )
        assert "Sentiment: Positive (score=0.800)" in out
        assert "Reply (engine=groq):" in out

    def test_methods_are_optional(self):
        out = build_report(REVIEWS, SENTIMENTS, SCORES, REPLIES)
        assert "engine=" not in out
        assert "Sentiment: Positive (score=0.800)" in out
        assert "Reply:" in out

    def test_returns_string_not_path(self):
        # Previously this wrote a file to downloads/ and read it back.
        out = build_report(REVIEWS, SENTIMENTS, SCORES, REPLIES, METHODS)
        assert isinstance(out, str)
        assert len(out) > 50

    def test_has_generated_header(self):
        out = build_report(REVIEWS, SENTIMENTS, SCORES, REPLIES, METHODS)
        assert "App Review Assistant report" in out
        assert "UTC" in out

    def test_empty_input_still_renders_header(self):
        out = build_report([], [], [], [])
        assert "App Review Assistant report" in out

    def test_unicode_survives(self):
        hindi = "बहुत बढ़िया"
        thanks = "धन्यवाद!"
        out = build_report([hindi], ["Positive"], [0.8], [thanks], ["groq"])
        assert hindi in out
        assert thanks in out


class TestBuildReportFilename:
    def test_shape(self):
        name = build_report_filename("app_reviews")
        assert re.fullmatch(r"app_reviews_reviews_\d{8}_\d{6}\.txt", name)

    @pytest.mark.parametrize(
        "label,prefix",
        [("my app!", "myapp"), ("../../etc/passwd", "etcpasswd"), ("", "app")],
    )
    def test_sanitizes_label(self, label, prefix):
        assert build_report_filename(label).startswith(prefix + "_reviews_")

    def test_no_path_separators(self):
        name = build_report_filename("a/b\\c")
        assert "/" not in name and "\\" not in name
