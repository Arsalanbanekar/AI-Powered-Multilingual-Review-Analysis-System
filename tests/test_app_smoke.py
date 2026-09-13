"""Smoke tests that actually execute app.py through Streamlit's test harness.

These drive the real widgets, so they catch runtime errors the unit tests and a
plain import check cannot.
"""

from pathlib import Path

import pytest

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

MANUAL_MODE = "Manual paste"
TIMEOUT = 60

PASTED = "This app is amazing!\nCrashes every time I open it.\nUI is okay."


@pytest.fixture
def app(monkeypatch):
    """Run the app with Groq disabled so tests stay offline and deterministic.

    The clients are built at import time, so patching the env var alone is not
    enough once a real key is present in .env - the module objects themselves
    have to be cleared.
    """
    import src.llm.reply_generator as rg
    import src.models.sentiment_model as sm

    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setattr(sm, "client", None)
    monkeypatch.setattr(rg, "client", None)

    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    return at


def _to_manual(at):
    at.selectbox[0].set_value(MANUAL_MODE).run()
    return at


class TestBoot:
    def test_app_runs_without_exception(self, app):
        assert not app.exception

    def test_shows_empty_state_prompt(self, app):
        assert any("Fetch or paste reviews" in i.value for i in app.info)

    def test_does_not_leak_key_status_to_the_ui(self, app):
        # The old build rendered "GROQ KEY FOUND: True/False" to every visitor.
        rendered = " ".join(m.value for m in app.markdown) + " ".join(
            i.value for i in app.info
        )
        assert "KEY FOUND" not in rendered

    def test_play_mode_exposes_separate_review_and_reply_language(self, app):
        labels = [s.label for s in app.selectbox]
        assert "Review language" in labels
        assert "Reply language" in labels


class TestManualFlow:
    def test_switching_mode_shows_text_area(self, app):
        at = _to_manual(app)
        assert not at.exception
        assert len(at.text_area) == 1

    def test_analyze_pasted_reviews(self, app):
        at = _to_manual(app)
        at.text_area[0].set_value(PASTED).run()
        at.button[0].click().run()

        assert not at.exception
        assert any("Loaded 3 reviews" in s.value for s in at.success)
        assert any("Sentiment summary" in h.value for h in at.subheader)

    def test_degradation_is_surfaced(self, app):
        # With no API key every row falls back to TextBlob; the UI must say so
        # instead of silently mixing engines.
        at = _to_manual(app)
        at.text_area[0].set_value(PASTED).run()
        at.button[0].click().run()
        assert any("TextBlob" in w.value for w in at.warning)

    def test_generate_replies_then_download_survives_rerun(self, app):
        at = _to_manual(app)
        at.text_area[0].set_value(PASTED).run()
        at.button[0].click().run()

        generate = [b for b in at.button if "Generate replies" in b.label]
        assert generate, "generate button missing"
        generate[0].click().run()
        assert not at.exception
        assert any("Replies generated" in s.value for s in at.success)

        # Regression: the download button used to live inside the generate
        # button's if-block, so it vanished on the next rerun.
        assert len(at.download_button) == 1

        at.run()
        assert not at.exception
        assert len(at.download_button) == 1, "download button lost on rerun"

    def test_replies_are_stored_as_text_method_pairs(self, app):
        # AppTest cannot read the deferred download payload, so verify the
        # session state the download button is built from, then render it.
        at = _to_manual(app)
        at.text_area[0].set_value(PASTED).run()
        at.button[0].click().run()
        [b for b in at.button if "Generate replies" in b.label][0].click().run()

        stored = at.session_state["replies"]
        assert len(stored) == 3
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in stored)

        from src.utils.file_generator import build_report

        report = build_report(
            at.session_state["reviews"],
            ["Positive"] * 3,
            [0.8] * 3,
            [text for text, _ in stored],
            reply_methods=[method for _, method in stored],
        )
        assert "App Review Assistant report" in report
        assert "This app is amazing!" in report
        assert "engine=template" in report

    def test_download_button_is_enabled(self, app):
        at = _to_manual(app)
        at.text_area[0].set_value(PASTED).run()
        at.button[0].click().run()
        [b for b in at.button if "Generate replies" in b.label][0].click().run()
        assert at.download_button[0].proto.disabled is False

    def test_empty_paste_is_rejected(self, app):
        at = _to_manual(app)
        at.text_area[0].set_value("   ").run()
        at.button[0].click().run()
        assert any("at least one review" in e.value for e in at.error)
        assert not at.exception
