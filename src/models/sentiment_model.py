"""Multilingual sentiment classification for app reviews.

Primary engine is Groq (LLaMA). TextBlob is the offline fallback. Both engines
report scores on the same scale (see LABEL_TO_SCORE) so the two are comparable,
and every result carries the name of the engine that produced it.
"""

import logging
import os
import random
import time
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq
from textblob import TextBlob

load_dotenv()

log = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Groq retires models periodically (llama-3.1-8b-instant now 404s), so this is
# overridable without a code change: set GROQ_MODEL.
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Reasoning models (gpt-oss, qwen3) spend part of the token budget on hidden
# reasoning before emitting any content. A small max_tokens therefore returns
# an empty string, so budgets here are sized for reasoning plus the answer, and
# reasoning_effort is kept low. The flag is only sent to models that accept it.
REASONING_MODEL_MARKERS = ("gpt-oss", "qwen3")


def _reasoning_kwargs() -> dict:
    if any(marker in MODEL for marker in REASONING_MODEL_MARKERS):
        return {"reasoning_effort": "low"}
    return {}

# Sized for reasoning overhead; the label itself is only a few tokens.
CLASSIFY_MAX_TOKENS = 512

ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

# Single scale shared by both engines, so the score column always means the
# same thing no matter which engine produced the row.
LABEL_TO_SCORE = {
    "Positive": 0.8,
    "Neutral": 0.0,
    "Negative": -0.5,
    "Highly Negative": -0.9,
}

# Engine names reported back to the caller.
METHOD_LLM = "groq"
METHOD_TEXTBLOB = "textblob"

MAX_ATTEMPTS = 3
BACKOFF_BASE = 1.5


def _normalize_label(text: str) -> str:
    """Map raw model output onto one of ALLOWED_LABELS.

    Exact matches win first. Only then do we fall back to substring sniffing,
    checking the two-word label before the single-word ones so that
    "Highly Negative" is not swallowed by the "neg" test.
    """
    if not text:
        return "Neutral"

    cleaned = text.strip().strip("\"'`.*").lower()

    for label in ALLOWED_LABELS:
        if cleaned == label.lower():
            return label

    # "not negative" / "positive, not negative" must not read as Negative, so
    # require the negation-free forms. Check the compound label first.
    if "high" in cleaned and "neg" in cleaned:
        return "Highly Negative"
    if "pos" in cleaned:
        return "Positive"
    if "neu" in cleaned:
        return "Neutral"
    if "neg" in cleaned:
        return "Negative"
    return "Neutral"


def _is_rate_limit(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    if status == 429:
        return True
    return "rate" in str(exc).lower() and "limit" in str(exc).lower()


PROMPT = """You are analyzing user reviews for an app. The review can be in any language
(English, Hindi, Hinglish, German, etc.).

Classify the OVERALL sentiment of this review into exactly ONE of these labels.

- Positive: satisfied or praising, even if they mention a small nitpick.
- Neutral: factual, mixed, or a mild suggestion with no real dissatisfaction.
- Negative: dissatisfied. A concrete complaint such as bugs, crashes, ads,
  confusing UI, or poor performance.
- Highly Negative: severe distress or anger. Use this label when ANY of these
  apply, even if the review is short:
    * lost money, double charges, fraud or scam accusations, demands a refund
    * lost data, lost an account, or a privacy or security concern
    * rage, insults, all-caps shouting, or abusive language
    * threats to uninstall, leave, report the developer, or take legal action
    * says the app is unusable or the worst they have used

Judge severity by what the reviewer describes and how angry they are, not by
the length of the review.

Only answer with the label. Do not add anything else.

Review:
\"\"\"{review}\"\"\"
"""


def _classify_with_llm(review: str) -> Tuple[str, float, str]:
    """Classify one review with Groq, retrying on rate limits.

    Falls back to TextBlob if every attempt fails. The returned method name
    tells the caller which engine actually produced the label.
    """
    if client is None:
        return _classify_with_textblob(review)

    for attempt in range(MAX_ATTEMPTS):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": PROMPT.format(review=review)}],
                max_tokens=CLASSIFY_MAX_TOKENS,
                temperature=0,  # classification should be reproducible
                **_reasoning_kwargs(),
            )
            raw = (completion.choices[0].message.content or "").strip()
            if not raw:
                # Reasoning models can burn the whole budget on hidden tokens
                # and return nothing; _normalize_label("") would quietly call
                # that Neutral, so treat it as a failure instead.
                raise ValueError("empty completion from model")
            label = _normalize_label(raw)
            return label, LABEL_TO_SCORE[label], METHOD_LLM

        except Exception as exc:
            last = attempt == MAX_ATTEMPTS - 1
            if _is_rate_limit(exc) and not last:
                delay = BACKOFF_BASE ** attempt + random.uniform(0, 0.3)
                log.warning("Groq rate limited, retrying in %.1fs", delay)
                time.sleep(delay)
                continue
            log.warning("Groq classification failed (%s); using TextBlob", exc)
            return _classify_with_textblob(review)

    return _classify_with_textblob(review)


def _classify_with_textblob(review: str) -> Tuple[str, float, str]:
    """Offline fallback. Tuned for English; a rough signal elsewhere."""
    try:
        polarity = TextBlob(review).sentiment.polarity
    except Exception as exc:
        log.warning("TextBlob failed on review (%s); defaulting to Neutral", exc)
        return "Neutral", LABEL_TO_SCORE["Neutral"], METHOD_TEXTBLOB

    if polarity > 0.2:
        label = "Positive"
    elif -0.2 <= polarity <= 0.2:
        label = "Neutral"
    elif polarity < -0.6:
        label = "Highly Negative"
    else:
        label = "Negative"

    return label, LABEL_TO_SCORE[label], METHOD_TEXTBLOB


def analyze_sentiments(
    reviews: List[str],
) -> Tuple[List[str], List[float], List[str]]:
    """Classify every review.

    Returns three parallel lists: labels, scores, and the engine used per
    review, so the caller can tell the user when results were degraded.
    """
    sentiments: List[str] = []
    scores: List[float] = []
    methods: List[str] = []

    use_llm = client is not None
    log.info("Sentiment engine: %s", METHOD_LLM if use_llm else METHOD_TEXTBLOB)

    for review in reviews:
        if use_llm:
            label, score, method = _classify_with_llm(review)
        else:
            label, score, method = _classify_with_textblob(review)

        sentiments.append(label)
        scores.append(score)
        methods.append(method)

    return sentiments, scores, methods
