"""Tests for reply generation. No network required."""

import pytest

from src.llm import reply_generator as rg


def _fake_client(content):
    """Minimal stand-in for the Groq client returning a fixed completion."""

    class Fake:
        class chat:
            class completions:
                @staticmethod
                def create(**_):
                    class M:
                        pass

                    m = M()
                    m.content = content

                    class C:
                        message = m

                    class R:
                        choices = [C()]

                    return R()

    return Fake


class TestTemplateReply:
    @pytest.mark.parametrize(
        "sentiment,marker",
        [
            ("Positive", "Thank you for your positive feedback"),
            ("Neutral", "Thank you for sharing your thoughts"),
            ("Highly Negative", "very sorry"),
            ("Negative", "sorry you faced an issue"),
        ],
    )
    def test_tone_per_sentiment(self, sentiment, marker):
        out = rg._template_reply("my review", sentiment)
        assert marker in out
        assert "my review" in out

    def test_unknown_sentiment_uses_negative_template(self):
        assert "sorry you faced an issue" in rg._template_reply("r", "Bogus")


class TestGenerateReply:
    def test_no_client_returns_template(self, monkeypatch):
        monkeypatch.setattr(rg, "client", None)
        text, method = rg.generate_reply("Great app", "Positive")
        assert method == rg.METHOD_TEMPLATE
        assert "Thank you" in text

    def test_returns_text_and_method_pair(self, monkeypatch):
        monkeypatch.setattr(rg, "client", _fake_client("  Thanks for the kind words!  "))
        text, method = rg.generate_reply("Great app", "Positive", "en")
        assert text == "Thanks for the kind words!"
        assert method == rg.METHOD_LLM

    def test_empty_model_output_falls_back(self, monkeypatch):
        monkeypatch.setattr(rg, "client", _fake_client("   "))
        monkeypatch.setattr(rg, "MAX_ATTEMPTS", 1)
        _, method = rg.generate_reply("Great app", "Positive")
        assert method == rg.METHOD_TEMPLATE

    def test_none_model_output_falls_back(self, monkeypatch):
        monkeypatch.setattr(rg, "client", _fake_client(None))
        monkeypatch.setattr(rg, "MAX_ATTEMPTS", 1)
        _, method = rg.generate_reply("Great app", "Positive")
        assert method == rg.METHOD_TEMPLATE

    def test_api_error_falls_back(self, monkeypatch):
        class Boom:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        raise RuntimeError("groq down")

        monkeypatch.setattr(rg, "client", Boom)
        monkeypatch.setattr(rg, "MAX_ATTEMPTS", 1)
        text, method = rg.generate_reply("Great app", "Positive")
        assert method == rg.METHOD_TEMPLATE
        assert "Thank you" in text

    def test_rate_limit_is_retried_then_succeeds(self, monkeypatch):
        calls = {"n": 0}

        class Flaky:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        calls["n"] += 1
                        if calls["n"] == 1:
                            exc = RuntimeError("rate limit exceeded")
                            exc.status_code = 429
                            raise exc

                        class M:
                            content = "Recovered reply"

                        class C:
                            message = M()

                        class R:
                            choices = [C()]

                        return R()

        monkeypatch.setattr(rg, "client", Flaky)
        monkeypatch.setattr(rg, "BACKOFF_BASE", 1.0)
        monkeypatch.setattr(rg.time, "sleep", lambda _: None)
        text, method = rg.generate_reply("Great app", "Positive")
        assert text == "Recovered reply"
        assert method == rg.METHOD_LLM
        assert calls["n"] == 2

    def test_non_rate_limit_error_is_not_retried(self, monkeypatch):
        calls = {"n": 0}

        class Boom:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        calls["n"] += 1
                        raise RuntimeError("invalid api key")

        monkeypatch.setattr(rg, "client", Boom)
        monkeypatch.setattr(rg.time, "sleep", lambda _: None)
        _, method = rg.generate_reply("Great app", "Positive")
        assert method == rg.METHOD_TEMPLATE
        assert calls["n"] == 1


class TestRateLimitDetection:
    def test_status_code(self):
        exc = Exception("x")
        exc.status_code = 429
        assert rg._is_rate_limit(exc)

    def test_message_text(self):
        assert rg._is_rate_limit(Exception("Rate limit reached"))

    def test_unrelated_error(self):
        assert not rg._is_rate_limit(Exception("bad request"))


class TestLanguageNaming:
    """Regression: a bare ISO code made the model guess.

    Asking for "hi" produced Indonesian ("id") in live testing, so the prompt
    now names the language explicitly.
    """

    @pytest.mark.parametrize(
        "code,name",
        [("en", "English"), ("hi", "Hindi"), ("de", "German"),
         ("fr", "French"), ("es", "Spanish")],
    )
    def test_known_codes_map_to_names(self, code, name):
        assert rg._language_name(code) == name

    def test_case_insensitive(self):
        assert rg._language_name("HI") == "Hindi"

    @pytest.mark.parametrize("code", [None, ""])
    def test_missing_code_defaults_to_english(self, code):
        assert rg._language_name(code) == "English"

    def test_unknown_code_passes_through(self):
        assert rg._language_name("pt") == "pt"

    def test_prompt_names_the_language_not_the_code(self, monkeypatch):
        captured = {}

        class Spy:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        captured["prompt"] = kwargs["messages"][0]["content"]

                        class M:
                            content = "ok"

                        class C:
                            message = M()

                        class R:
                            choices = [C()]

                        return R()

        monkeypatch.setattr(rg, "client", Spy)
        rg.generate_reply("review", "Positive", "hi")
        assert "Hindi" in captured["prompt"]
        assert 'code: "hi"' not in captured["prompt"]


class TestReasoningKwargs:
    def test_reasoning_flag_sent_to_gpt_oss(self, monkeypatch):
        monkeypatch.setattr(rg, "MODEL", "openai/gpt-oss-20b")
        assert rg._reasoning_kwargs() == {"reasoning_effort": "low"}

    def test_no_flag_for_non_reasoning_models(self, monkeypatch):
        monkeypatch.setattr(rg, "MODEL", "groq/compound-mini")
        assert rg._reasoning_kwargs() == {}


class TestPromptGuardrails:
    """The reply is posted publicly as the developer, so the prompt must not
    let the model invent contacts or commit to anything.

    Measured before the guardrails: 4/15 replies invented a support address
    (support@example.com), 2/15 promised a fix or timeline.
    """

    def test_forbids_inventing_contact_details(self):
        assert "Do NOT invent an email address" in rg.PROMPT

    def test_forbids_promises_and_timelines(self):
        assert "Do NOT promise a fix, refund, timeline" in rg.PROMPT

    def test_forbids_claiming_a_team_is_investigating(self):
        assert "claim a" in rg.PROMPT and "investigating" in rg.PROMPT

    def test_forbids_inventing_app_facts(self):
        assert "Do NOT invent facts about the app" in rg.PROMPT

    def test_requires_naming_the_specific_problem(self):
        assert "Name the SPECIFIC problem" in rg.PROMPT
        assert "generic apology" in rg.PROMPT

    def test_requires_acknowledging_impact(self):
        assert "Acknowledge how the problem affected them" in rg.PROMPT

    def test_guardrails_survive_formatting(self, monkeypatch):
        captured = {}

        class Spy:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        captured["p"] = kwargs["messages"][0]["content"]

                        class M:
                            content = "ok"

                        class C:
                            message = M()

                        class R:
                            choices = [C()]

                        return R()

        monkeypatch.setattr(rg, "client", Spy)
        rg.generate_reply("charged twice", "Highly Negative", "en")
        assert "Do NOT invent an email address" in captured["p"]
        assert "charged twice" in captured["p"]
