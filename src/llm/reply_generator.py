"""Generate polite developer replies to app reviews.

Primary engine is Groq (LLaMA); a static template is the fallback. The reply
language is supplied by the caller and is never auto-detected.
"""

import logging
import os
import random
import time
from typing import Tuple

from dotenv import load_dotenv
from groq import Groq

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

# Reasoning overhead plus a 2-3 sentence reply.
REPLY_MAX_TOKENS = 800

METHOD_LLM = "groq"
METHOD_TEMPLATE = "template"

MAX_ATTEMPTS = 3
BACKOFF_BASE = 1.5

# Models reply in the wrong language when handed a bare ISO code: asking for
# "hi" produced Indonesian ("id") in live testing. Name the language instead.
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
}


def _language_name(lang_code: str) -> str:
    return LANGUAGE_NAMES.get((lang_code or "en").lower(), lang_code)


TONES = {
    "Positive": "warm, appreciative, friendly",
    "Neutral": "curious, polite, open to feedback",
    "Highly Negative": "apologetic, serious, calm, solution-focused",
    "Negative": "apologetic, understanding, constructive",
}

PROMPT = """You are an app support agent replying to a user review.

REVIEW:
\"\"\"{review}\"\"\"

SENTIMENT: {sentiment}

LANGUAGE REQUIREMENT:
- Write the ENTIRE reply in {language} and in no other language.
- If the review is in a different language, IGNORE that and still write in {language}.
- Do NOT mention the language or talk about language detection.

STYLE INSTRUCTIONS:
- Tone: {tone}
- Length: 2-3 sentences.
- Name the SPECIFIC problem the reviewer described, in their own terms
  (e.g. the double charge, the battery drain, the login failure). Never answer
  with a generic apology that would fit any review.
- Acknowledge how the problem affected them before offering next steps.

NEVER DO THESE:
- Do NOT invent an email address, URL, phone number, or support handle. If the
  reviewer needs to reach support, say so WITHOUT naming a contact.
- Do NOT promise a fix, refund, timeline, or release date, and do NOT claim a
  team is already investigating. You cannot commit on the developer's behalf.
- Do NOT invent facts about the app, its features, or its pricing.
- Do NOT explain your reasoning, show examples, or translate anything.

Just write the final reply text.
"""


def _is_rate_limit(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    if status == 429:
        return True
    return "rate" in str(exc).lower() and "limit" in str(exc).lower()


def _template_reply(review: str, sentiment: str, lang_code: str = "en") -> str:
    """Static fallback used when Groq is unavailable. Always English."""
    if sentiment == "Positive":
        return (
            "Thank you for your positive feedback! We're glad you're enjoying "
            f"the app.\n\nReview: {review}"
        )

    if sentiment == "Neutral":
        return (
            "Thank you for sharing your thoughts. If you have any suggestions, "
            f"we'd love to hear them.\n\nReview: {review}"
        )

    if sentiment == "Highly Negative":
        return (
            "We're very sorry to hear about your experience. It sounds like a serious issue, "
            "and we want to fix it quickly. Please share your device details and what exactly "
            f"went wrong.\n\nReview: {review}"
        )

    return (
        "We're sorry you faced an issue while using the app. "
        "Please share a few more details so we can understand and improve.\n\n"
        f"Review: {review}"
    )


def generate_reply(
    review: str, sentiment: str, lang_code: str = "en"
) -> Tuple[str, str]:
    """Generate one reply.

    Returns (reply_text, method) so the caller can tell the user when replies
    fell back to the static template instead of the LLM.
    """
    if client is None:
        return _template_reply(review, sentiment, lang_code), METHOD_TEMPLATE

    tone = TONES.get(sentiment, TONES["Negative"])
    prompt = PROMPT.format(
        review=review,
        sentiment=sentiment,
        language=_language_name(lang_code),
        tone=tone,
    )

    for attempt in range(MAX_ATTEMPTS):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=REPLY_MAX_TOKENS,
                **_reasoning_kwargs(),
            )
            reply_text = (completion.choices[0].message.content or "").strip()
            if not reply_text:
                raise ValueError("empty reply from model")
            return reply_text, METHOD_LLM

        except Exception as exc:
            last = attempt == MAX_ATTEMPTS - 1
            if _is_rate_limit(exc) and not last:
                delay = BACKOFF_BASE ** attempt + random.uniform(0, 0.3)
                log.warning("Groq rate limited, retrying in %.1fs", delay)
                time.sleep(delay)
                continue
            log.warning("Groq reply failed (%s); using template", exc)
            return _template_reply(review, sentiment, lang_code), METHOD_TEMPLATE

    return _template_reply(review, sentiment, lang_code), METHOD_TEMPLATE
