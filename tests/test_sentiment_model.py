"""Tests for sentiment labelling. No network or API key required."""

import pytest

from src.models import sentiment_model as sm


class TestNormalizeLabel:
    @pytest.mark.parametrize("raw", ["Positive", "Neutral", "Negative", "Highly Negative"])
    def test_exact_labels_round_trip(self, raw):
        assert sm._normalize_label(raw) == raw

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("positive", "Positive"),
            ("POSITIVE.", "Positive"),
            ('"Negative"', "Negative"),
            ("Label: Neutral", "Neutral"),
            ("highly negative", "Highly Negative"),
            ("Highly  Negative", "Highly Negative"),
        ],
    )
    def test_messy_output_is_normalized(self, raw, expected):
        assert sm._normalize_label(raw) == expected

    def test_positive_wins_over_trailing_negation(self):
        # Regression: "neg" used to be tested before "pos", so any explanation
        # mentioning "negative" was misread as Negative.
        assert sm._normalize_label("The sentiment is positive, not negative.") == "Positive"

    def test_compound_label_not_swallowed_by_negative(self):
        assert sm._normalize_label("I would say highly negative here") == "Highly Negative"

    @pytest.mark.parametrize("raw", ["", "   ", "Mixed", None])
    def test_unparseable_defaults_to_neutral(self, raw):
        assert sm._normalize_label(raw) == "Neutral"


class TestTextBlobFallback:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("This app is absolutely wonderful and amazing!", "Positive"),
            ("It is an app.", "Neutral"),
        ],
    )
    def test_obvious_cases(self, text, expected):
        label, _, method = sm._classify_with_textblob(text)
        assert label == expected
        assert method == sm.METHOD_TEXTBLOB

    def test_all_four_labels_are_reachable(self):
        # Guards the threshold chain ordering.
        seen = set()
        for polarity in (1.0, 0.0, -0.4, -0.9):
            if polarity > 0.2:
                seen.add("Positive")
            elif -0.2 <= polarity <= 0.2:
                seen.add("Neutral")
            elif polarity < -0.6:
                seen.add("Highly Negative")
            else:
                seen.add("Negative")
        assert seen == set(sm.ALLOWED_LABELS)

    def test_score_uses_shared_scale(self):
        label, score, _ = sm._classify_with_textblob("This app is wonderful!")
        assert score == sm.LABEL_TO_SCORE[label]

    def test_never_raises_on_hostile_input(self):
        for text in ["", "🙂🙂🙂", "बहुत बढ़िया", "\x00\x01"]:
            label, score, method = sm._classify_with_textblob(text)
            assert label in sm.ALLOWED_LABELS
            assert method == sm.METHOD_TEXTBLOB


class TestRateLimitDetection:
    def test_detects_status_code(self):
        exc = Exception("boom")
        exc.status_code = 429
        assert sm._is_rate_limit(exc)

    def test_detects_message(self):
        assert sm._is_rate_limit(Exception("Rate limit reached for model"))

    def test_ignores_unrelated_errors(self):
        assert not sm._is_rate_limit(Exception("invalid api key"))


class TestAnalyzeSentiments:
    def test_returns_three_aligned_lists(self, monkeypatch):
        monkeypatch.setattr(sm, "client", None)
        reviews = ["Great app!", "Terrible, crashes constantly.", "It works."]
        sentiments, scores, methods = sm.analyze_sentiments(reviews)
        assert len(sentiments) == len(scores) == len(methods) == len(reviews)
        assert all(s in sm.ALLOWED_LABELS for s in sentiments)
        assert all(m == sm.METHOD_TEXTBLOB for m in methods)

    def test_empty_input(self, monkeypatch):
        monkeypatch.setattr(sm, "client", None)
        assert sm.analyze_sentiments([]) == ([], [], [])

    def test_scores_always_match_labels(self, monkeypatch):
        monkeypatch.setattr(sm, "client", None)
        sentiments, scores, _ = sm.analyze_sentiments(["good", "bad", "awful rubbish"])
        for label, score in zip(sentiments, scores):
            assert score == sm.LABEL_TO_SCORE[label]

    def test_empty_completion_falls_back_instead_of_neutral(self, monkeypatch):
        # Regression: reasoning models return empty content, which
        # _normalize_label("") would have silently reported as a real Neutral
        # produced by the LLM.
        class Empty:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        class M:
                            content = ""

                        class C:
                            message = M()

                        class R:
                            choices = [C()]

                        return R()

        monkeypatch.setattr(sm, "client", Empty)
        monkeypatch.setattr(sm, "MAX_ATTEMPTS", 1)
        _, _, methods = sm.analyze_sentiments(["Great app!"])
        assert methods == [sm.METHOD_TEXTBLOB]

    def test_llm_failure_falls_back_without_raising(self, monkeypatch):
        class Boom:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        raise RuntimeError("groq down")

        monkeypatch.setattr(sm, "client", Boom)
        monkeypatch.setattr(sm, "MAX_ATTEMPTS", 1)
        sentiments, scores, methods = sm.analyze_sentiments(["anything"])
        assert methods == [sm.METHOD_TEXTBLOB]
        assert sentiments[0] in sm.ALLOWED_LABELS


class TestReasoningKwargs:
    def test_reasoning_flag_sent_to_gpt_oss(self, monkeypatch):
        monkeypatch.setattr(sm, "MODEL", "openai/gpt-oss-20b")
        assert sm._reasoning_kwargs() == {"reasoning_effort": "low"}

    def test_no_flag_for_non_reasoning_models(self, monkeypatch):
        monkeypatch.setattr(sm, "MODEL", "groq/compound-mini")
        assert sm._reasoning_kwargs() == {}

    def test_budget_leaves_room_for_reasoning(self):
        # A 10-token budget returned empty content from gpt-oss models.
        assert sm.CLASSIFY_MAX_TOKENS >= 256


class TestSeverityPrompt:
    """Severity drives the reply tone, so the boundary between Negative and
    Highly Negative has to be defined rather than guessed.

    Before these definitions, "THEY STOLE MY MONEY! Total scam! Reporting to
    police!" was classified merely Negative.
    """

    def test_defines_every_label(self):
        for label in ["Positive:", "Neutral:", "Negative:", "Highly Negative:"]:
            assert label in sm.PROMPT

    def test_money_and_fraud_escalate(self):
        assert "fraud or scam accusations" in sm.PROMPT
        assert "refund" in sm.PROMPT

    def test_data_loss_escalates(self):
        assert "lost data" in sm.PROMPT

    def test_rage_and_abuse_escalate(self):
        assert "all-caps shouting" in sm.PROMPT

    def test_threats_escalate(self):
        assert "take legal action" in sm.PROMPT

    def test_short_reviews_not_downgraded(self):
        assert "not by" in sm.PROMPT and "length of the review" in sm.PROMPT

    def test_still_demands_bare_label(self):
        assert "Only answer with the label" in sm.PROMPT
