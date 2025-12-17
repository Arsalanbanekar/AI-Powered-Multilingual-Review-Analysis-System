
# import streamlit as st
# import pandas as pd
# import os
# print("API KEY FOUND:", bool(os.getenv("OPENAI_API_KEY")))


# from src.reviews.playstore_fetcher import fetch_playstore_reviews
# from src.models.sentiment_model import analyze_sentiments
# from src.llm.reply_generator import generate_reply
# from src.utils.file_generator import save_replies_to_txt

# st.set_page_config(page_title="App Review Assistant", layout="wide")

# st.title("📱 App Review Assistant")
# st.write("Analyze app reviews from Google Play or paste your own reviews, then generate polite AI replies.")

# mode = st.selectbox(
#     "Select input method",
#     ["Google Play (Android app)", "Manual paste"]
# )

# reviews = []

# if mode == "Google Play (Android app)":
#     pkg = st.text_input("Enter Android app package name (e.g., com.whatsapp, com.instagram.android)")
#     col1, col2 = st.columns(2)
#     with col1:
#         limit = st.number_input("Number of reviews to fetch", min_value=5, max_value=200, value=20, step=5)
#     with col2:
#         lang = st.text_input("Language code", value="en")
#     country = st.text_input("Country code", value="in")

#     if st.button("Fetch & Analyze"):
#         if not pkg.strip():
#             st.error("Please enter a valid app package name.")
#         else:
#             with st.spinner("Fetching reviews from Google Play..."):
#                 try:
#                     reviews = fetch_playstore_reviews(pkg.strip(), int(limit), lang=lang.strip(), country=country.strip())
#                 except Exception as e:
#                     st.error(f"Failed to fetch reviews: {e}")
#                     reviews = []

#         if not reviews:
#             st.warning("No reviews fetched. Try a different app, language, or country.")
#         else:
#             st.success(f"Fetched {len(reviews)} reviews.")
# elif mode == "Manual paste":
#     raw = st.text_area(
#         "Paste reviews here (one review per line)",
#         height=200,
#         placeholder="This app is amazing!\nCrashes every time I open it.\nUI is okay but could be better."
#     )
#     if st.button("Analyze pasted reviews"):
#         lines = [r.strip() for r in raw.split("\n") if r.strip()]
#         if not lines:
#             st.error("Please paste at least one review.")
#         else:
#             reviews = lines
#             st.success(f"Loaded {len(reviews)} reviews from pasted text.")

# # If we have reviews, run analysis block
# if reviews:
#     with st.spinner("Running sentiment analysis..."):
#         sentiments, scores = analyze_sentiments(reviews)

#     df = pd.DataFrame({
#         "review": reviews,
#         "sentiment": sentiments,
#         "score": scores,
#     })

#     st.subheader("Sentiment summary")
#     st.write(df["sentiment"].value_counts())

#     st.subheader("Sample reviews")
#     for i, row in df.head(5).iterrows():
#         st.markdown(f"**Review {i+1} — {row['sentiment']} ({row['score']:.2f})**")
#         st.caption(row["review"])

#     st.subheader("Generate AI replies")
#     st.info("If your OPENAI_API_KEY is set, replies will be generated using GPT-4.1-mini. Otherwise, a simple template reply is used as fallback.")

#     if st.button("Generate replies for all reviews"):
#         with st.spinner("Generating replies..."):
#             replies = [generate_reply(r, s) for r, s in zip(reviews, sentiments)]
#         df["reply"] = replies

#         st.success("Replies generated.")
#         st.dataframe(df.head(20))

#         filename = "app_reviews_with_replies.txt"
#         path = save_replies_to_txt("app_reviews", reviews, sentiments, scores, replies)
#         with open(path, "r", encoding="utf-8") as f:
#             st.download_button(
#                 "📥 Download all replies as .txt",
#                 data=f.read(),
#                 file_name=filename,
#                 mime="text/plain"
#             )



# import streamlit as st
# import pandas as pd
# from src.reviews.playstore_fetcher import fetch_playstore_reviews
# from src.models.sentiment_model import analyze_sentiments
# from src.llm.reply_generator import generate_reply
# from src.utils.file_generator import save_replies_to_txt
# from src.reviews.package_lookup import get_package_from_app_name

# import os

# st.set_page_config(page_title="App Review Assistant", layout="wide")

# st.title("📱 App Review Assistant")
# st.write("Analyze app reviews from Google Play or paste your own reviews, then generate polite AI replies.")

# # --- DEBUG (you added this earlier, optional) ---
# # st.write("API KEY FOUND:", bool(os.getenv("OPENAI_API_KEY")))
# st.write("GROQ KEY FOUND:", bool(os.getenv("GROQ_API_KEY")))
# # ------------------------------------------------

# # Initialize session state for reviews
# if "reviews" not in st.session_state:
#     st.session_state["reviews"] = []

# mode = st.selectbox(
#     "Select input method",
#     ["Google Play (Android app)", "Manual paste"]
# )

# # ---------- INPUT SECTION ----------
# # if mode == "Google Play (Android app)":
# #     pkg = st.text_input("Enter Android app package name (e.g., com.whatsapp, com.instagram.android)")
# #     col1, col2 = st.columns(2)
# #     with col1:
# #         limit = st.number_input("Number of reviews to fetch", min_value=5, max_value=200, value=20, step=5)
# #     with col2:
# #         lang = st.text_input("Language code", value="en")
# #     country = st.text_input("Country code", value="in")

# #     if st.button("Fetch & Analyze"):
# #         if not pkg.strip():
# #             st.error("Please enter a valid app package name.")
# #         else:
# #             with st.spinner("Fetching reviews from Google Play..."):
# #                 try:
# #                     reviews = fetch_playstore_reviews(pkg.strip(), int(limit), lang=lang.strip(), country=country.strip())
# #                 except Exception as e:
# #                     st.error(f"Failed to fetch reviews: {e}")
# #                     reviews = []

# #             if not reviews:
# #                 st.warning("No reviews fetched. Try a different app, language, or country.")
# #             else:
# #                 st.session_state["reviews"] = reviews
# #                 st.success(f"Fetched {len(reviews)} reviews.")

# if mode == "Google Play (Android app)":
#     app_name = st.text_input("Enter App Name (e.g., Netflix, WhatsApp, Instagram)")
#     col1, col2 = st.columns(2)
#     with col1:
#         limit = st.number_input("Number of reviews to fetch", min_value=5, max_value=200, value=20, step=5)
#     with col2:
#         lang = st.text_input("Language code", value="en")
#     country = st.text_input("Country code", value="in")

#     if st.button("Fetch & Analyze"):
#         if not app_name.strip():
#             st.error("Please enter a valid app name.")
#         else:
#             # 1) Resolve app name -> package id
#             with st.spinner("Searching app on Google Play..."):
#                 pkg = get_package_from_app_name(app_name.strip(), lang=lang.strip(), country=country.strip())

#             if not pkg:
#                 st.error("Could not find any app with that name. Try a different name or adjust language/country.")
#             else:
#                 st.info(f"Using package: {pkg}")
#                 # 2) Fetch reviews using the resolved package id
#                 with st.spinner("Fetching reviews from Google Play..."):
#                     try:
#                         reviews = fetch_playstore_reviews(pkg, int(limit), lang=lang.strip(), country=country.strip())
#                     except Exception as e:
#                         st.error(f"Failed to fetch reviews: {e}")
#                         reviews = []

#                 if not reviews:
#                     st.warning("No reviews fetched. Try a different app, language, or country.")
#                 else:
#                     st.session_state["reviews"] = reviews
#                     st.success(f"Fetched {len(reviews)} reviews.")


# # elif mode == "Manual paste":
# #     raw = st.text_area(
# #         "Paste reviews here (one review per line)",
# #         height=200,
# #         placeholder="This app is amazing!\nCrashes every time I open it.\nUI is okay but could be better."
# #     )
# #     if st.button("Analyze pasted reviews"):
# #         lines = [r.strip() for r in raw.split("\n") if r.strip()]
# #         if not lines:
# #             st.error("Please paste at least one review.")
# #         else:
# #             st.session_state["reviews"] = lines
# #             st.success(f"Loaded {len(lines)} reviews from pasted text.")

# elif mode == "Manual paste":
#     raw = st.text_area(
#         "Paste reviews here (one review per line)",
#         height=200,
#         placeholder="This app is amazing!\nCrashes every time I open it.\nUI is okay but could be better."
#     )

#     # NEW: reply language dropdown for manual paste mode
#     reply_lang_manual = st.selectbox(
#         "Select reply language (for AI replies)",
#         ["en", "hi", "de", "fr", "es"],
#         index=0,
#     )
#     # store it so we can use it later when generating replies
#     st.session_state["reply_lang"] = reply_lang_manual

#     if st.button("Analyze pasted reviews"):
#         lines = [r.strip() for r in raw.split("\n") if r.strip()]
#         if not lines:
#             st.error("Please paste at least one review.")
#         else:
#             st.session_state["reviews"] = lines
#             st.success(f"Loaded {len(lines)} reviews from pasted text.")


# # ---------- ANALYSIS + REPLY SECTION ----------
# reviews = st.session_state["reviews"]

# if reviews:
#     # Sentiment analysis
#     sentiments, scores = analyze_sentiments(reviews)

#     df = pd.DataFrame({
#         "review": reviews,
#         "sentiment": sentiments,
#         "score": scores,
#     })

#     st.subheader("Sentiment summary")
#     st.write(df["sentiment"].value_counts())

#     st.subheader("Sample reviews")
#     for i, row in df.head(5).iterrows():
#         st.markdown(f"**Review {i+1} — {row['sentiment']} ({row['score']:.2f})**")
#         st.caption(row["review"])

#     st.subheader("Generate AI replies")
#     st.info( "If your GROQ_API_KEY is set, replies will be generated using Groq (LLaMA models). "
#         "Otherwise, a simple fallback reply template is used.")

#     # if st.button("Generate replies for all reviews"):
#     #     with st.spinner("Generating replies..."):
#     #         replies = [generate_reply(r, s) for r, s in zip(reviews, sentiments)]
#     # if st.button("Generate replies for all reviews"):
#     #  with st.spinner("Generating replies..."):
#     #     replies = [generate_reply(r, s, lang) for r, s in zip(reviews, sentiments)]
#     #     df["reply"] = replies
#     if st.button("Generate replies for all reviews"):
#     # Use reply language from session; default to English if not set
#        reply_lang = st.session_state.get("reply_lang", "en")

#     with st.spinner("Generating replies..."):
#         replies = [generate_reply(r, s, reply_lang) for r, s in zip(reviews, sentiments)]


#         st.success("Replies generated.")
#         st.dataframe(df.head(20))

#         filename = "app_reviews_with_replies.txt"
#         path = save_replies_to_txt("app_reviews", reviews, sentiments, scores, replies)
#         with open(path, "r", encoding="utf-8") as f:
#             st.download_button(
#                 "📥 Download all replies as .txt",
#                 data=f.read(),
#                 file_name=filename,
#                 mime="text/plain"
#             )
# else:
#     st.info("Fetch or paste reviews above to begin.")





import streamlit as st
import pandas as pd
import os

from src.reviews.playstore_fetcher import fetch_playstore_reviews
from src.models.sentiment_model import analyze_sentiments
from src.llm.reply_generator import generate_reply
from src.utils.file_generator import save_replies_to_txt
from src.reviews.package_lookup import get_package_from_app_name

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="App Review Assistant", layout="wide")

st.title("📱 App Review Assistant")
st.write("Analyze app reviews from Google Play or paste your own reviews, then generate polite AI replies.")

# Debug info for Groq key
st.write("GROQ KEY FOUND:", bool(os.getenv("GROQ_API_KEY")))

# ----------------- SESSION INIT -----------------
if "reviews" not in st.session_state:
    st.session_state["reviews"] = []

if "reply_lang" not in st.session_state:
    st.session_state["reply_lang"] = "en"

# ----------------- MODE SELECT -----------------
mode = st.selectbox(
    "Select input method",
    ["Google Play (Android app)", "Manual paste"]
)

# ----------------- INPUT SECTION -----------------
if mode == "Google Play (Android app)":
    app_name = st.text_input("Enter App Name (e.g., Netflix, WhatsApp, Instagram)")
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input(
            "Number of reviews to fetch",
            min_value=5,
            max_value=200,
            value=20,
            step=5
        )
    with col2:
        lang = st.text_input("Language code (for reviews & replies)", value="en")
        # store reply language for later use
        st.session_state["reply_lang"] = lang

    country = st.text_input("Country code", value="in")

    if st.button("Fetch & Analyze"):
        if not app_name.strip():
            st.error("Please enter a valid app name.")
        else:
            # 1) Resolve app name -> package id
            with st.spinner("Searching app on Google Play..."):
                pkg = get_package_from_app_name(
                    app_name.strip(),
                    lang=lang.strip(),
                    country=country.strip()
                )

            if not pkg:
                st.error("Could not find any app with that name. Try a different name or adjust language/country.")
            else:
                st.info(f"Using package: {pkg}")

                # 2) Fetch reviews using the resolved package id
                with st.spinner("Fetching reviews from Google Play..."):
                    try:
                        reviews = fetch_playstore_reviews(
                            pkg,
                            int(limit),
                            lang=lang.strip(),
                            country=country.strip()
                        )
                    except Exception as e:
                        st.error(f"Failed to fetch reviews: {e}")
                        reviews = []

                if not reviews:
                    st.warning("No reviews fetched. Try a different app, language, or country.")
                else:
                    st.session_state["reviews"] = reviews
                    st.success(f"Fetched {len(reviews)} reviews.")

elif mode == "Manual paste":
    raw = st.text_area(
        "Paste reviews here (one review per line)",
        height=200,
        placeholder="This app is amazing!\nCrashes every time I open it.\nUI is okay but could be better."
    )

    # Reply language control just for manual mode
    reply_lang_manual = st.selectbox(
        "Select reply language (for AI replies)",
        ["en", "hi", "de", "fr", "es"],
        index=0,
    )
    st.session_state["reply_lang"] = reply_lang_manual

    if st.button("Analyze pasted reviews"):
        lines = [r.strip() for r in raw.split("\n") if r.strip()]
        if not lines:
            st.error("Please paste at least one review.")
        else:
            st.session_state["reviews"] = lines
            st.success(f"Loaded {len(lines)} reviews from pasted text.")

# ----------------- ANALYSIS + REPLY SECTION -----------------
reviews = st.session_state["reviews"]

if reviews:
    # Sentiment analysis
    sentiments, scores = analyze_sentiments(reviews)

    df = pd.DataFrame({
        "review": reviews,
        "sentiment": sentiments,
        "score": scores,
    })

    st.subheader("Sentiment summary")
    st.write(df["sentiment"].value_counts())

    st.subheader("Sample reviews")
    for i, row in df.head(5).iterrows():
        st.markdown(f"**Review {i+1} — {row['sentiment']} ({row['score']:.2f})**")
        st.caption(row["review"])

    st.subheader("Generate AI replies")
    st.info(
        "If your GROQ_API_KEY is set, replies will be generated using Groq (LLaMA models). "
        "Otherwise, a simple fallback reply template is used."
    )

    if st.button("Generate replies for all reviews"):
        # Use reply language from session; default to English if not set
        reply_lang = st.session_state.get("reply_lang", "en")

        with st.spinner("Generating replies..."):
            replies = [generate_reply(r, s, reply_lang) for r, s in zip(reviews, sentiments)]
        df["reply"] = replies

        st.success("Replies generated.")
        st.dataframe(df.head(20))

        filename = "app_reviews_with_replies.txt"
        path = save_replies_to_txt("app_reviews", reviews, sentiments, scores, replies)
        with open(path, "r", encoding="utf-8") as f:
            st.download_button(
                "📥 Download all replies as .txt",
                data=f.read(),
                file_name=filename,
                mime="text/plain"
            )
else:
    st.info("Fetch or paste reviews above to begin.")
