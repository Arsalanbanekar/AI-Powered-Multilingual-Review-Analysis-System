"""App Review Assistant - fetch Play Store reviews, analyse sentiment, draft replies."""

import logging

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.llm.reply_generator import METHOD_TEMPLATE, generate_reply
from src.models.sentiment_model import METHOD_TEXTBLOB, analyze_sentiments
from src.reviews.package_lookup import get_package_from_app_name
from src.reviews.playstore_fetcher import fetch_playstore_reviews
from src.utils.file_generator import build_report, build_report_filename

load_dotenv()
logging.basicConfig(level=logging.INFO)

PLAY_MODE = "Google Play (Android app)"
MANUAL_MODE = "Manual paste"

# Languages offered for the generated replies.
REPLY_LANGUAGES = ["en", "hi", "de", "fr", "es"]

st.set_page_config(page_title="App Review Assistant", layout="wide")

st.title("📱 App Review Assistant")
st.write(
    "Analyze app reviews from Google Play or paste your own reviews, "
    "then generate polite AI replies."
)

# ----------------- SESSION INIT -----------------
st.session_state.setdefault("reviews", [])
st.session_state.setdefault("reply_lang", "en")
st.session_state.setdefault("replies", None)
st.session_state.setdefault("replies_key", None)
st.session_state.setdefault("mode", PLAY_MODE)


def reset_results() -> None:
    """Drop analysed output so stale replies never outlive their reviews."""
    st.session_state["replies"] = None
    st.session_state["replies_key"] = None


@st.cache_data(show_spinner=False)
def cached_analyze(reviews: tuple):
    """Cache sentiment by review content.

    Streamlit reruns this script on every widget interaction, so without this
    every keystroke re-classified every review - one API call per review, per
    interaction.
    """
    return analyze_sentiments(list(reviews))


# ----------------- MODE SELECT -----------------
mode = st.selectbox("Select input method", [PLAY_MODE, MANUAL_MODE])

if mode != st.session_state["mode"]:
    # Switching modes used to leave the previous batch in session state, which
    # then got re-analysed under the new mode's settings.
    st.session_state["mode"] = mode
    st.session_state["reviews"] = []
    reset_results()

# ----------------- INPUT SECTION -----------------
if mode == PLAY_MODE:
    app_name = st.text_input("Enter App Name (e.g., Netflix, WhatsApp, Instagram)")

    col1, col2, col3 = st.columns(3)
    with col1:
        limit = st.number_input(
            "Number of reviews to fetch", min_value=5, max_value=200, value=20, step=5
        )
    with col2:
        # Which reviews to fetch from the store.
        lang = st.selectbox("Review language", REPLY_LANGUAGES, index=0)
    with col3:
        # Independent of the fetch language, so you can read English reviews
        # and answer in Hindi.
        st.session_state["reply_lang"] = st.selectbox(
            "Reply language", REPLY_LANGUAGES, index=0
        )

    country = st.text_input("Country code", value="in")

    if st.button("Fetch & Analyze"):
        if not app_name.strip():
            st.error("Please enter a valid app name.")
        else:
            with st.spinner("Searching app on Google Play..."):
                pkg = get_package_from_app_name(
                    app_name.strip(), lang=lang.strip(), country=country.strip()
                )

            if not pkg:
                st.error(
                    "Could not find any app with that name. "
                    "Try a different name or adjust language/country."
                )
            else:
                st.info(f"Using package: {pkg}")
                reviews = []
                with st.spinner("Fetching reviews from Google Play..."):
                    try:
                        reviews = fetch_playstore_reviews(
                            pkg,
                            int(limit),
                            lang=lang.strip(),
                            country=country.strip(),
                        )
                    except Exception as exc:
                        st.error(f"Failed to fetch reviews: {exc}")

                if not reviews:
                    st.warning(
                        "No reviews fetched. Try a different app, language, or country."
                    )
                else:
                    st.session_state["reviews"] = reviews
                    reset_results()
                    st.success(f"Fetched {len(reviews)} reviews.")

elif mode == MANUAL_MODE:
    raw = st.text_area(
        "Paste reviews here (one review per line)",
        height=200,
        placeholder=(
            "This app is amazing!\nCrashes every time I open it.\n"
            "UI is okay but could be better."
        ),
    )

    st.session_state["reply_lang"] = st.selectbox(
        "Select reply language (for AI replies)", REPLY_LANGUAGES, index=0
    )

    if st.button("Analyze pasted reviews"):
        lines = [r.strip() for r in raw.split("\n") if r.strip()]
        if not lines:
            st.error("Please paste at least one review.")
        else:
            st.session_state["reviews"] = lines
            reset_results()
            st.success(f"Loaded {len(lines)} reviews from pasted text.")

# ----------------- ANALYSIS + REPLY SECTION -----------------
reviews = st.session_state["reviews"]

if not reviews:
    st.info("Fetch or paste reviews above to begin.")
    st.stop()

try:
    with st.spinner("Analyzing sentiment..."):
        sentiments, scores, methods = cached_analyze(tuple(reviews))
except Exception as exc:
    st.error(f"Sentiment analysis failed: {exc}")
    st.stop()

degraded = sum(1 for m in methods if m == METHOD_TEXTBLOB)
if degraded:
    st.warning(
        f"{degraded} of {len(methods)} reviews fell back to offline TextBlob "
        "scoring (Groq unavailable or rate limited). Those rows are less "
        "accurate on non-English reviews."
    )

df = pd.DataFrame(
    {
        "review": reviews,
        "sentiment": sentiments,
        "score": scores,
        "engine": methods,
    }
)

st.subheader("Sentiment summary")
st.write(df["sentiment"].value_counts())

st.subheader("Sample reviews")
for i, row in df.head(5).iterrows():
    st.markdown(f"**Review {i + 1} - {row['sentiment']} ({row['score']:.2f})**")
    st.caption(row["review"])

st.subheader("Generate AI replies")
st.info(
    "If your GROQ_API_KEY is set, replies will be generated using Groq (LLaMA models). "
    "Otherwise, a simple fallback reply template is used."
)

reply_lang = st.session_state["reply_lang"]
current_key = (tuple(reviews), reply_lang)

if st.button("Generate replies for all reviews"):
    with st.spinner("Generating replies..."):
        generated = [
            generate_reply(r, s, reply_lang) for r, s in zip(reviews, sentiments)
        ]
    # Persist in session state so clicking download (which triggers a rerun)
    # no longer discards the replies.
    st.session_state["replies"] = generated
    st.session_state["replies_key"] = current_key
    st.success("Replies generated.")

if st.session_state["replies"] and st.session_state["replies_key"] == current_key:
    replies = [text for text, _ in st.session_state["replies"]]
    reply_methods = [method for _, method in st.session_state["replies"]]

    templated = sum(1 for m in reply_methods if m == METHOD_TEMPLATE)
    if templated:
        st.warning(
            f"{templated} of {len(reply_methods)} replies used the static English "
            "template because Groq was unavailable or rate limited."
        )

    df["reply"] = replies
    st.dataframe(df.head(20))

    st.download_button(
        "📥 Download all replies as .txt",
        data=build_report(
            reviews,
            sentiments,
            scores,
            replies,
            sentiment_methods=methods,
            reply_methods=reply_methods,
        ),
        file_name=build_report_filename("app_reviews"),
        mime="text/plain",
    )
elif st.session_state["replies"]:
    st.info("Reviews or reply language changed - generate replies again.")
