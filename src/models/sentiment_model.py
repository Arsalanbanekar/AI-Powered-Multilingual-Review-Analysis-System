
# from typing import List, Tuple
# from textblob import TextBlob

# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """Return (sentiments, scores) for each review using TextBlob polarity.

#     Sentiment labels: Positive / Negative / Neutral
#     Score: polarity [-1.0, 1.0]
#     """
#     sentiments = []
#     scores = []
#     for r in reviews:
#         blob = TextBlob(r)
#         polarity = blob.sentiment.polarity
#         scores.append(polarity)
#         if polarity > 0.1:
#             sentiments.append("Positive")
#         elif polarity < -0.1:
#             sentiments.append("Negative")
#         else:
#             sentiments.append("Neutral")
#     return sentiments, scores






# from typing import List, Tuple
# from textblob import TextBlob

# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """
#     Return (sentiments, scores) for each review using TextBlob polarity.

#     Sentiment labels:
#       - Positive
#       - Neutral
#       - Negative
#       - Highly Negative

#     Score: polarity in [-1.0, 1.0]
#     """
#     sentiments = []
#     scores = []

#     for r in reviews:
#         blob = TextBlob(r)
#         polarity = blob.sentiment.polarity  # -1.0 (very negative) to 1.0 (very positive)
#         scores.append(polarity)

#         # You can tune these thresholds as you like:
#         if polarity > 0.2:
#             label = "Positive"
#         elif -0.2 <= polarity <= 0.2:
#             label = "Neutral"
#         elif -0.6 <= polarity < -0.2:
#             label = "Negative"
#         else:  # polarity < -0.6
#             label = "Highly Negative"

#         sentiments.append(label)

#     return sentiments, scores




# from typing import List, Tuple
# from textblob import TextBlob
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Try importing OpenAI client
# try:
#     from openai import OpenAI
#     _api_key = os.getenv("OPENAI_API_KEY")
#     _client = OpenAI(api_key=_api_key) if _api_key else None
# except Exception:
#     _client = None


# ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]


# def _classify_with_llm(review: str) -> Tuple[str, float]:
#     """
#     Use GPT (gpt-4.1-mini) to classify sentiment into:
#       - Positive
#       - Neutral
#       - Negative
#       - Highly Negative

#     Also return a rough score between -1 and 1.
#     """

#     if _client is None:
#         # Fallback: just neutral if no client
#         return "Neutral", 0.0

#     prompt = f"""
#     You are analyzing user reviews for an app in any language (English, Hindi, Hinglish, German, etc.).

#     For the review below, classify the overall sentiment into exactly ONE of:
#     - Positive
#     - Neutral
#     - Negative
#     - Highly Negative

#     Also give an intensity score between -1.0 and 1.0, where:
#     -1.0 = extremely negative, 0 = neutral, 1.0 = extremely positive.

#     Review: \"\"\"{review}\"\"\"

#     Respond ONLY in valid JSON, like:
#     {{"label": "Negative", "score": -0.7}}
#     """

#     try:
#         resp = _client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=60,
#         )
#         text = resp.choices[0].message.content.strip()
#         # Try parsing JSON safely
#         import json
#         data = json.loads(text)
#         label = data.get("label", "Neutral")
#         score = float(data.get("score", 0.0))

#         # Normalize label
#         if label not in ALLOWED_LABELS:
#             # try to clean up
#             label_clean = label.strip().lower()
#             if "high" in label_clean and "neg" in label_clean:
#                 label = "Highly Negative"
#             elif "neg" in label_clean:
#                 label = "Negative"
#             elif "pos" in label_clean:
#                 label = "Positive"
#             elif "neu" in label_clean:
#                 label = "Neutral"
#             else:
#                 label = "Neutral"

#         return label, score
#     except Exception:
#         # If anything goes wrong with LLM, fall back to neutral
#         return "Neutral", 0.0


# def _classify_with_textblob(review: str) -> Tuple[str, float]:
#     """
#     Fallback for when LLM is not available.
#     Works best for English, but okay as backup.
#     """
#     blob = TextBlob(review)
#     polarity = blob.sentiment.polarity  # -1 to 1

#     if polarity > 0.2:
#         label = "Positive"
#     elif -0.2 <= polarity <= 0.2:
#         label = "Neutral"
#     elif -0.6 <= polarity < -0.2:
#         label = "Negative"
#     else:  # polarity < -0.6
#         label = "Highly Negative"

#     return label, polarity


# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """
#     Return (sentiments, scores) for each review.

#     Uses GPT if OPENAI_API_KEY is set, otherwise falls back to TextBlob.
#     """
#     sentiments: List[str] = []
#     scores: List[float] = []

#     use_llm = _client is not None

#     for r in reviews:
#         if use_llm:
#             label, score = _classify_with_llm(r)
#         else:
#             label, score = _classify_with_textblob(r)

#         sentiments.append(label)
#         scores.append(score)

#     return sentiments, scores



# from typing import List, Tuple
# from textblob import TextBlob
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Try importing OpenAI client
# try:
#     from openai import OpenAI
#     _api_key = os.getenv("OPENAI_API_KEY")
#     _client = OpenAI(api_key=_api_key) if _api_key else None
# except Exception:
#     _client = None

# ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

# def _classify_with_llm(review: str) -> Tuple[str, float]:
#     """Use GPT for multilingual sentiment classification."""
#     if _client is None:
#         return "Neutral", 0.0

#     prompt = f"""
#     You are analyzing user reviews in ANY language (English, Hindi, Hinglish, German, etc.)

#     Classify the sentiment into exactly one of these:
#     - Positive
#     - Neutral
#     - Negative
#     - Highly Negative

#     Also return an emotion intensity score between -1.0 and 1.0.

#     Review:
#     \"\"\"{review}\"\"\"

#     Respond ONLY in valid JSON:
#     {{"label": "Negative", "score": -0.72}}
#     """

#     try:
#         resp = _client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=60,
#         )
#         import json
#         data = json.loads(resp.choices[0].message.content)

#         label = data.get("label", "Neutral")
#         score = float(data.get("score", 0))

#         # Validate label
#         if label not in ALLOWED_LABELS:
#             label_lower = label.lower()
#             if "high" in label_lower and "neg" in label_lower:
#                 label = "Highly Negative"
#             elif "neg" in label_lower:
#                 label = "Negative"
#             elif "pos" in label_lower:
#                 label = "Positive"
#             else:
#                 label = "Neutral"

#         return label, score

#     except Exception:
#         return "Neutral", 0.0


# def _classify_with_textblob(review: str) -> Tuple[str, float]:
#     """Fallback sentiment when GPT is not available."""
#     blob = TextBlob(review)
#     polarity = blob.sentiment.polarity

#     if polarity > 0.2:
#         label = "Positive"
#     elif -0.2 <= polarity <= 0.2:
#         label = "Neutral"
#     elif polarity < -0.6:
#         label = "Highly Negative"
#     else:
#         label = "Negative"

#     return label, polarity


# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """Use GPT if available, otherwise fallback to TextBlob."""
#     sentiments = []
#     scores = []

#     use_llm = _client is not None

#     for r in reviews:
#         if use_llm:
#             label, score = _classify_with_llm(r)
#         else:
#             label, score = _classify_with_textblob(r)

#         sentiments.append(label)
#         scores.append(score)

#     return sentiments, scores






# from typing import List, Tuple
# from textblob import TextBlob
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Try importing OpenAI client
# try:
#     from openai import OpenAI
#     _api_key = os.getenv("OPENAI_API_KEY")
#     _client = OpenAI(api_key=_api_key) if _api_key else None
# except Exception:
#     _client = None

# ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

# LABEL_TO_SCORE = {
#     "Positive": 0.8,
#     "Neutral": 0.0,
#     "Negative": -0.5,
#     "Highly Negative": -0.9,
# }


# def _normalize_label(text: str) -> str:
#     text = text.strip().lower()
#     if "high" in text and "neg" in text:
#         return "Highly Negative"
#     if "neg" in text:
#         return "Negative"
#     if "pos" in text:
#         return "Positive"
#     if "neu" in text:
#         return "Neutral"
#     # fallback
#     return "Neutral"


# def _classify_with_llm(review: str) -> Tuple[str, float]:
#     """
#     Use GPT for multilingual sentiment classification.
#     GPT must answer with exactly one of:
#     Positive / Neutral / Negative / Highly Negative
#     """

#     if _client is None:
#         return "Neutral", 0.0

#     prompt = f"""
#     You are analyzing user reviews for an app. The review can be in any language (English, Hindi, Hinglish, German, etc.).

#     Classify the OVERALL sentiment of this review into exactly ONE of these labels:
#     - Positive
#     - Neutral
#     - Negative
#     - Highly Negative

#     Only answer with the label. Do not add anything else.

#     Review:
#     \"\"\"{review}\"\"\"
#     """

#     try:
#         resp = _client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=10,
#         )
#         raw = resp.choices[0].message.content.strip()
#         label = _normalize_label(raw)
#         score = LABEL_TO_SCORE.get(label, 0.0)
#         return label, score
#     except Exception:
#         # If anything goes wrong with the API, fall back to neutral
#         return "Neutral", 0.0


# def _classify_with_textblob(review: str) -> Tuple[str, float]:
#     """
#     Fallback sentiment when GPT is not available.
#     Works best for English, but okay as backup.
#     """
#     blob = TextBlob(review)
#     polarity = blob.sentiment.polarity  # -1 to 1

#     if polarity > 0.2:
#         label = "Positive"
#     elif -0.2 <= polarity <= 0.2:
#         label = "Neutral"
#     elif polarity < -0.6:
#         label = "Highly Negative"
#     else:
#         label = "Negative"

#     return label, polarity


# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """
#     Return (sentiments, scores) for each review.

#     Uses GPT if OPENAI_API_KEY is set, otherwise falls back to TextBlob.
#     """
#     sentiments: List[str] = []
#     scores: List[float] = []

#     use_llm = _client is not None

#     for r in reviews:
#         if use_llm:
#             label, score = _classify_with_llm(r)
#         else:
#             label, score = _classify_with_textblob(r)

#         sentiments.append(label)
#         scores.append(score)

#     return sentiments, scores





# from typing import List, Tuple
# from textblob import TextBlob
# import os
# from dotenv import load_dotenv
# import openai  # <— use module style

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

# LABEL_TO_SCORE = {
#     "Positive": 0.8,
#     "Neutral": 0.0,
#     "Negative": -0.5,
#     "Highly Negative": -0.9,
# }


# def _normalize_label(text: str) -> str:
#     text = text.strip().lower()
#     if "high" in text and "neg" in text:
#         return "Highly Negative"
#     if "neg" in text:
#         return "Negative"
#     if "pos" in text:
#         return "Positive"
#     if "neu" in text:
#         return "Neutral"
#     return "Neutral"


# def _classify_with_llm(review: str) -> Tuple[str, float]:
#     """
#     Use GPT for multilingual sentiment classification.

#     GPT must answer with exactly one of:
#     Positive / Neutral / Negative / Highly Negative
#     """

#     if not openai.api_key:
#         # no API key -> no LLM
#         return "Neutral", 0.0

#     prompt = f"""
#     You are analyzing user reviews for an app. The review can be in any language
#     (English, Hindi, Hinglish, German, etc.).

#     Classify the OVERALL sentiment of this review into exactly ONE of these labels:
#     - Positive
#     - Neutral
#     - Negative
#     - Highly Negative

#     Only answer with the label. Do not add anything else.

#     Review:
#     \"\"\"{review}\"\"\"
#     """

#     try:
#         resp = openai.ChatCompletion.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=10,
#         )
#         raw = resp["choices"][0]["message"]["content"].strip()
#         # DEBUG: you can uncomment this to see what the model returns
#         # print("LLM RAW LABEL:", repr(raw))

#         label = _normalize_label(raw)
#         score = LABEL_TO_SCORE.get(label, 0.0)
#         return label, score
#     except Exception as e:
#         # DEBUG: see what's going wrong
#         print("LLM classification error:", repr(e))
#         return "Neutral", 0.0


# def _classify_with_textblob(review: str) -> Tuple[str, float]:
#     """
#     Fallback sentiment when GPT is not available.
#     Works best for English, but okay as backup.
#     """
#     blob = TextBlob(review)
#     polarity = blob.sentiment.polarity  # -1 to 1

#     if polarity > 0.2:
#         label = "Positive"
#     elif -0.2 <= polarity <= 0.2:
#         label = "Neutral"
#     elif polarity < -0.6:
#         label = "Highly Negative"
#     else:
#         label = "Negative"

#     return label, polarity


# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """
#     Return (sentiments, scores) for each review.

#     Uses GPT if OPENAI_API_KEY is set and works, otherwise falls back to TextBlob.
#     """
#     sentiments: List[str] = []
#     scores: List[float] = []

#     use_llm = bool(openai.api_key)
#     # DEBUG: see once in your terminal
#     print("USE_LLM_FOR_SENTIMENT:", use_llm)

#     for r in reviews:
#         if use_llm:
#             label, score = _classify_with_llm(r)
#         else:
#             label, score = _classify_with_textblob(r)

#         sentiments.append(label)
#         scores.append(score)

#     return sentiments, scores







# from typing import List, Tuple
# from textblob import TextBlob
# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()

# client = OpenAI()  # uses OPENAI_API_KEY from env

# ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

# LABEL_TO_SCORE = {
#     "Positive": 0.8,
#     "Neutral": 0.0,
#     "Negative": -0.5,
#     "Highly Negative": -0.9,
# }


# def _normalize_label(text: str) -> str:
#     text = text.strip().lower()
#     if "high" in text and "neg" in text:
#         return "Highly Negative"
#     if "neg" in text:
#         return "Negative"
#     if "pos" in text or "positiv" in text:
#         return "Positive"
#     if "neu" in text:
#         return "Neutral"
#     # fallback
#     return "Neutral"


# def _classify_with_llm(review: str) -> Tuple[str, float]:
#     """
#     Use GPT (via OpenAI v1 client) for multilingual sentiment classification.

#     Model must answer with exactly one of:
#     Positive / Neutral / Negative / Highly Negative
#     """

#     # If key is missing, client will throw – we catch it below
#     prompt = f"""
#     You are analyzing user reviews for an app. The review can be in any language
#     (English, Hindi, Hinglish, German, etc.).

#     Classify the OVERALL sentiment of this review into exactly ONE of these labels:
#     - Positive
#     - Neutral
#     - Negative
#     - Highly Negative

#     Only answer with the label. Do not add anything else.

#     Review:
#     \"\"\"{review}\"\"\"
#     """

#     try:
#         completion = client.chat.completions.create(
#             # safer widely-supported model
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=10,
#         )
#         raw = completion.choices[0].message.content.strip()
#         print("LLM RAW LABEL:", repr(raw))  # DEBUG so you can see what it outputs

#         label = _normalize_label(raw)
#         score = LABEL_TO_SCORE.get(label, 0.0)
#         return label, score

#     except Exception as e:
#         # VERY IMPORTANT: show why it failed
#         print("LLM classification error:", repr(e))
#         return "Neutral", 0.0


# def _classify_with_textblob(review: str) -> Tuple[str, float]:
#     """
#     Fallback sentiment when GPT is not available.
#     Works best for English, but okay as backup.
#     """
#     blob = TextBlob(review)
#     polarity = blob.sentiment.polarity  # -1 to 1

#     if polarity > 0.2:
#         label = "Positive"
#     elif -0.2 <= polarity <= 0.2:
#         label = "Neutral"
#     elif polarity < -0.6:
#         label = "Highly Negative"
#     else:
#         label = "Negative"

#     return label, polarity


# def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
#     """
#     Return (sentiments, scores) for each review.

#     Uses GPT if possible, otherwise falls back to TextBlob.
#     """
#     sentiments: List[str] = []
#     scores: List[float] = []

#     # simple check: do we have any api key at all?
#     use_llm = bool(os.getenv("OPENAI_API_KEY"))
#     print("USE_LLM_FOR_SENTIMENT:", use_llm)

#     for r in reviews:
#         if use_llm:
#             label, score = _classify_with_llm(r)
#         else:
#             label, score = _classify_with_textblob(r)

#         sentiments.append(label)
#         scores.append(score)

#     return sentiments, scores



from typing import List, Tuple
from textblob import TextBlob
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

ALLOWED_LABELS = ["Positive", "Neutral", "Negative", "Highly Negative"]

LABEL_TO_SCORE = {
    "Positive": 0.8,
    "Neutral": 0.0,
    "Negative": -0.5,
    "Highly Negative": -0.9,
}


def _normalize_label(text: str) -> str:
    text = text.strip().lower()
    if "high" in text and "neg" in text:
        return "Highly Negative"
    if "neg" in text:
        return "Negative"
    if "pos" in text or "positiv" in text:
        return "Positive"
    if "neu" in text:
        return "Neutral"
    return "Neutral"


def _classify_with_llm(review: str) -> Tuple[str, float]:
    """
    Use Groq (LLaMA) for multilingual sentiment classification.

    Model must answer with exactly one of:
    Positive / Neutral / Negative / Highly Negative
    """
    if client is None:
        # no key -> no LLM
        return "Neutral", 0.0

    prompt = f"""
    You are analyzing user reviews for an app. The review can be in any language
    (English, Hindi, Hinglish, German, etc.).

    Classify the OVERALL sentiment of this review into exactly ONE of these labels:
    - Positive
    - Neutral
    - Negative
    - Highly Negative

    Only answer with the label. Do not add anything else.

    Review:
    \"\"\"{review}\"\"\"
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # fast, good for classification
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
        )
        raw = completion.choices[0].message.content.strip()
        print("GROQ RAW LABEL:", repr(raw))  # DEBUG

        label = _normalize_label(raw)
        score = LABEL_TO_SCORE.get(label, 0.0)
        return label, score

    except Exception as e:
        print("GROQ classification error:", repr(e))
        # Fall back to TextBlob if anything goes wrong
        return _classify_with_textblob(review)


def _classify_with_textblob(review: str) -> Tuple[str, float]:
    """
    Fallback sentiment when LLM is not available.
    Works best for English, but okay as backup.
    """
    blob = TextBlob(review)
    polarity = blob.sentiment.polarity  # -1 to 1

    if polarity > 0.2:
        label = "Positive"
    elif -0.2 <= polarity <= 0.2:
        label = "Neutral"
    elif polarity < -0.6:
        label = "Highly Negative"
    else:
        label = "Negative"

    return label, polarity


def analyze_sentiments(reviews: List[str]) -> Tuple[List[str], List[float]]:
    """
    Return (sentiments, scores) for each review.

    Uses Groq if GROQ_API_KEY is set, otherwise falls back to TextBlob.
    """
    sentiments: List[str] = []
    scores: List[float] = []

    use_llm = client is not None
    print("USE_GROQ_FOR_SENTIMENT:", use_llm)

    for r in reviews:
        if use_llm:
            label, score = _classify_with_llm(r)
        else:
            label, score = _classify_with_textblob(r)

        sentiments.append(label)
        scores.append(score)

    return sentiments, scores
