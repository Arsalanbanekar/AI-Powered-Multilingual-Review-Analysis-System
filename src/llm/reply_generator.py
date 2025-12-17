
# from typing import Optional
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Try importing OpenAI client
# try:
#     from openai import OpenAI
#     _api_key = os.getenv("OPENAI_API_KEY")
#     _client: Optional[OpenAI] = OpenAI(api_key=_api_key) if _api_key else None
# except Exception:
#     _client = None

# def _template_reply(review: str, sentiment: str) -> str:
#     """Fallback reply if no API key or OpenAI not available."""
#     if sentiment == "Positive":
#         return f"Thank you for your positive review! We're glad you are enjoying the app.\n\nReview: {review}"
#     elif sentiment == "Negative":
#         return (
#             "We're sorry to hear about your negative experience. "
#             "We appreciate your feedback and will work to improve future versions of the app.\n\n"
#             f"Review: {review}"
#         )
#     else:
#         return (
#             "Thank you for taking the time to leave a review. "
#             "We value your feedback and will keep working to make the app better.\n\n"
#             f"Review: {review}"
#         )

# def generate_reply(review: str, sentiment: str) -> str:
#     """Generate a polite reply using GPT-4.1-mini if possible, otherwise use a simple template."""
#     if _client is None:
#         return _template_reply(review, sentiment)

#     try:
#         prompt = (
#             "You are a polite and professional app developer responding to user reviews on the app store.\n"
#             f"Review: {review}\n"
#             f"Detected sentiment: {sentiment}\n\n"
#             "Write a short, friendly, and helpful reply (2-4 sentences). "
#             "If the sentiment is negative, apologize and show willingness to improve. "
#             "If positive, thank the user and encourage them to keep using the app."
#         )

#         resp = _client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=180
#         )
#         content = resp.choices[0].message.content.strip()
#         return content
#     except Exception:
#         # If anything goes wrong with the API, fall back
#         return _template_reply(review, sentiment)







# from typing import Optional
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Try importing OpenAI client
# try:
#     from openai import OpenAI
#     _api_key = os.getenv("OPENAI_API_KEY")
#     _client: Optional[OpenAI] = OpenAI(api_key=_api_key) if _api_key else None
# except Exception:
#     _client = None


# def _template_reply(review: str, sentiment: str) -> str:
#     """
#     Fallback reply if no API key or OpenAI not available.
#     Different behaviour for Positive / Neutral / Negative / Highly Negative.
#     """
#     if sentiment == "Positive":
#         return (
#             "Thank you so much for your positive review! We're really glad you are enjoying the app. "
#             "Your support motivates us to keep improving.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Neutral":
#         return (
#             "Thank you for taking the time to leave a review. "
#             "If you have any specific suggestions on how we can improve the app, "
#             "we’d love to hear them.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Highly Negative":
#         return (
#             "We're really sorry to hear about your experience. "
#             "Your feedback is very important, and it looks like you faced a serious issue. "
#             "Please share more details (device, app version, and what exactly went wrong) so we can investigate and fix this as soon as possible. "
#             "You can also reach out to our support team directly from the app settings.\n\n"
#             f"Review: {review}"
#         )

#     # Default for 'Negative' and anything else
#     return (
#         "We're sorry that you had a negative experience with the app. "
#         "Thank you for pointing this out. If you can share a bit more information about the issue "
#         "(what you were doing when it happened, any error messages, etc.), "
#         "it will help us understand the problem and improve future versions.\n\n"
#         f"Review: {review}"
#     )


# # def generate_reply(review: str, sentiment: str) -> str:
# #     """
# #     Generate a polite reply using GPT-4.1-mini if possible,
# #     otherwise use a simple category-aware template.
# #     """
# #     if _client is None:
# #         return _template_reply(review, sentiment)

# #     # Different tone instructions depending on sentiment
# #     if sentiment == "Positive":
# #         style_instruction = (
# #             "Be warm and thankful. Appreciate their support and briefly reinforce a key feature they liked."
# #         )
# #     elif sentiment == "Neutral":
# #         style_instruction = (
# #             "Be appreciative but curious. Thank them and gently invite them to share more specific suggestions "
# #             "so developers can improve the app."
# #         )
# #     elif sentiment == "Highly Negative":
# #         style_instruction = (
# #             "Be very apologetic, calm, and solution-focused. Assume the user may be frustrated. "
# #             "Acknowledge the seriousness of their issue, ask for key details (device, app version, steps to reproduce), "
# #             "and tell them that the feedback will be passed on to the development team."
# #         )
# #     else:  # Negative
# #         style_instruction = (
# #             "Be apologetic and constructive. Acknowledge their frustration, apologize, and ask for a bit more detail "
# #             "so developers can understand and fix the issue in future updates."
# #         )

# #     try:
# #         prompt = (
# #             "You are an app developer or support agent responding to user reviews on the app store.\n\n"
# #             f"Review: {review}\n"
# #             f"Detected sentiment category: {sentiment}\n\n"
# #             f"Response style: {style_instruction}\n\n"
# #             "Write a short, friendly, and helpful reply (2–4 sentences). "
# #             "Focus on improving user experience and also encouraging the user to give enough details "
# #             "so that developers can act on the feedback. "
# #             "Do NOT invent technical details; keep it generic but empathetic."
# #         )

# #         resp = _client.chat.completions.create(
# #             model="gpt-4.1-mini",
# #             messages=[{"role": "user", "content": prompt}],
# #             max_tokens=220,
# #         )
# #         content = resp.choices[0].message.content.strip()
# #         return content
# #     except Exception:
# #         # If anything goes wrong with the API, fall back
# #         return _template_reply(review, sentiment)



# def generate_reply(review: str, sentiment: str) -> str:
#     """
#     Generate a polite reply using GPT-4.1-mini if possible,
#     otherwise use a simple category-aware template.

#     GPT is instructed to reply in the SAME LANGUAGE as the review.
#     """

#     if _client is None:
#         return _template_reply(review, sentiment)

#     # Different tone instructions depending on sentiment
#     if sentiment == "Positive":
#         style_instruction = (
#             "Be warm and thankful. Appreciate their support and briefly reinforce a key feature they liked."
#         )
#     elif sentiment == "Neutral":
#         style_instruction = (
#             "Be appreciative but curious. Thank them and gently invite them to share more specific suggestions "
#             "so developers can improve the app."
#         )
#     elif sentiment == "Highly Negative":
#         style_instruction = (
#             "Be very apologetic, calm, and solution-focused. Assume the user may be frustrated. "
#             "Acknowledge the seriousness of their issue, ask for key details (device, app version, steps to reproduce), "
#             "and tell them that the feedback will be passed on to the development team."
#         )
#     else:  # Negative
#         style_instruction = (
#             "Be apologetic and constructive. Acknowledge their frustration, apologize, and ask for a bit more detail "
#             "so developers can understand and fix the issue in future updates."
#         )

#     try:
#         prompt = (
#             "You are an app developer or support agent responding to user reviews on the app store.\n\n"
#             f"User review (in original language): {review}\n"
#             f"Detected sentiment category: {sentiment}\n\n"
#             f"Response style: {style_instruction}\n\n"
#             "Very important:\n"
#             "- First, automatically detect the language of the review.\n"
#             "- Reply in the SAME LANGUAGE as the review (if the review is in Hindi, reply in Hindi; if German, reply in German; etc.).\n"
#             "- If the review mixes multiple languages, use the dominant language.\n\n"
#             "Write a short, friendly, and helpful reply (2–4 sentences). "
#             "Focus on improving user experience and also encouraging the user to give enough details "
#             "so that developers can act on the feedback. "
#             "Do NOT invent technical details; keep it generic but empathetic."
#         )

#         resp = _client.chat.completions.create(
#             model="gpt-4.1-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=220,
#         )
#         content = resp.choices[0].message.content.strip()
#         return content
#     except Exception:
#         return _template_reply(review, sentiment)



# from typing import Optional
# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()
# client = OpenAI()  # uses OPENAI_API_KEY


# def _template_reply(review: str, sentiment: str) -> str:
#     """
#     Fallback reply if no API key or OpenAI not available.
#     Different behaviour for Positive / Neutral / Negative / Highly Negative.
#     """
#     if sentiment == "Positive":
#         return (
#             "Thank you so much for your positive review! We're really glad you are enjoying the app. "
#             "Your support motivates us to keep improving.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Neutral":
#         return (
#             "Thank you for taking the time to leave a review. "
#             "If you have any specific suggestions on how we can improve the app, "
#             "we’d love to hear them.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Highly Negative":
#         return (
#             "We're really sorry to hear about your experience. "
#             "Your feedback is very important, and it looks like you faced a serious issue. "
#             "Please share more details (device, app version, and what exactly went wrong) so we can investigate and fix this as soon as possible. "
#             "You can also reach out to our support team directly from the app settings.\n\n"
#             f"Review: {review}"
#         )

#     # Default for 'Negative' and anything else
#     return (
#         "We're sorry that you had a negative experience with the app. "
#         "Thank you for pointing this out. If you can share a bit more information about the issue "
#         "(what you were doing when it happened, any error messages, etc.), "
#         "it will help us understand the problem and improve future versions.\n\n"
#         f"Review: {review}"
#     )


# def generate_reply(review: str, sentiment: str) -> str:
#     """
#     Generate a polite reply using GPT (v1 client) if possible,
#     otherwise use a simple category-aware template.

#     GPT is instructed to reply in the SAME LANGUAGE as the review.
#     """
#     if not os.getenv("OPENAI_API_KEY"):
#         # no key -> no LLM -> fallback
#         return _template_reply(review, sentiment)

#     # Different tone instructions depending on sentiment
#     if sentiment == "Positive":
#         style_instruction = (
#             "Be warm and thankful. Appreciate their support and briefly reinforce a key feature they liked."
#         )
#     elif sentiment == "Neutral":
#         style_instruction = (
#             "Be appreciative but curious. Thank them and gently invite them to share more specific suggestions "
#             "so developers can improve the app."
#         )
#     elif sentiment == "Highly Negative":
#         style_instruction = (
#             "Be very apologetic, calm, and solution-focused. Assume the user may be frustrated. "
#             "Acknowledge the seriousness of their issue, ask for key details (device, app version, steps to reproduce), "
#             "and tell them that the feedback will be passed on to the development team."
#         )
#     else:  # Negative
#         style_instruction = (
#             "Be apologetic and constructive. Acknowledge their frustration, apologize, and ask for a bit more detail "
#             "so developers can understand and fix the issue in future updates."
#         )

#     try:
#         prompt = (
#             "You are an app developer or support agent responding to user reviews on the app store.\n\n"
#             f"User review (in original language): {review}\n"
#             f"Detected sentiment category: {sentiment}\n\n"
#             f"Response style: {style_instruction}\n\n"
#             "Very important:\n"
#             "- First, automatically detect the language of the review.\n"
#             "- Reply in the SAME LANGUAGE as the review (if the review is in Hindi, reply in Hindi; if German, reply in German; etc.).\n"
#             "- If the review mixes multiple languages, use the dominant language.\n\n"
#             "Write a short, friendly, and helpful reply (2–4 sentences). "
#             "Focus on improving user experience and also encouraging the user to give enough details "
#             "so that developers can act on the feedback. "
#             "Do NOT invent technical details; keep it generic but empathetic."
#         )

#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=220,
#         )
#         content = completion.choices[0].message.content.strip()
#         print("LLM REPLY OK")  # DEBUG
#         return content
#     except Exception as e:
#         print("LLM reply error:", repr(e))
#         return _template_reply(review, sentiment)







# from typing import Optional
# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# def _template_reply(review: str, sentiment: str) -> str:
#     """
#     Fallback reply if no API key or Groq not available.
#     Different behaviour for Positive / Neutral / Negative / Highly Negative.
#     """
#     if sentiment == "Positive":
#         return (
#             "Thank you so much for your positive review! We're really glad you are enjoying the app. "
#             "Your support motivates us to keep improving.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Neutral":
#         return (
#             "Thank you for taking the time to leave a review. "
#             "If you have any specific suggestions on how we can improve the app, "
#             "we’d love to hear them.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Highly Negative":
#         return (
#             "We're really sorry to hear about your experience. "
#             "Your feedback is very important, and it looks like you faced a serious issue. "
#             "Please share more details (device, app version, and what exactly went wrong) so we can investigate and fix this as soon as possible. "
#             "You can also reach out to our support team directly from the app settings.\n\n"
#             f"Review: {review}"
#         )

#     # Default for 'Negative' and anything else
#     return (
#         "We're sorry that you had a negative experience with the app. "
#         "Thank you for pointing this out. If you can share a bit more information about the issue "
#         "(what you were doing when it happened, any error messages, etc.), "
#         "it will help us understand the problem and improve future versions.\n\n"
#         f"Review: {review}"
#     )


# def generate_reply(review: str, sentiment: str) -> str:
#     """
#     Generate a polite reply using Groq (LLaMA) if possible,
#     otherwise use a simple category-aware template.

#     LLM is instructed to reply in the SAME LANGUAGE as the review.
#     """
#     if client is None:
#         return _template_reply(review, sentiment)

#     # Different tone instructions depending on sentiment
#     if sentiment == "Positive":
#         style_instruction = (
#             "Be warm and thankful. Appreciate their support and briefly reinforce a key feature they liked."
#         )
#     elif sentiment == "Neutral":
#         style_instruction = (
#             "Be appreciative but curious. Thank them and gently invite them to share more specific suggestions "
#             "so developers can improve the app."
#         )
#     elif sentiment == "Highly Negative":
#         style_instruction = (
#             "Be very apologetic, calm, and solution-focused. Assume the user may be frustrated. "
#             "Acknowledge the seriousness of their issue, ask for key details (device, app version, steps to reproduce), "
#             "and tell them that the feedback will be passed on to the development team."
#         )
#     else:  # Negative
#         style_instruction = (
#             "Be apologetic and constructive. Acknowledge their frustration, apologize, and ask for a bit more detail "
#             "so developers can understand and fix the issue in future updates."
#         )

#     try:
#         prompt = (
#             "You are an app developer or support agent responding to user reviews on the app store.\n\n"
#             f"User review (in original language): {review}\n"
#             f"Detected sentiment category: {sentiment}\n\n"
#             f"Response style: {style_instruction}\n\n"
#             "Very important:\n"
#             "- First, automatically detect the language of the review.\n"
#             "- Reply in the SAME LANGUAGE as the review (if the review is in Hindi, reply in Hindi; if German, reply in German; etc.).\n"
#             "- If the review mixes multiple languages, use the dominant language.\n\n"
#             "Write a short, friendly, and helpful reply (2–4 sentences). "
#             "Focus on improving user experience and also encouraging the user to give enough details "
#             "so that developers can act on the feedback. "
#             "Do NOT invent technical details; keep it generic but empathetic."
#         )

#         completion = client.chat.completions.create(
#             model="llama-3.1-70b-versatile",  # better for generation, still free-tier friendly
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=220,
#         )
#         content = completion.choices[0].message.content.strip()
#         print("GROQ REPLY OK")  # DEBUG
#         return content
#     except Exception as e:
#         print("GROQ reply error:", repr(e))
#         return _template_reply(review, sentiment)







# from typing import Optional
# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# def _template_reply(review: str, sentiment: str) -> str:
#     """
#     Fallback reply if no API key or Groq not available.
#     Different behaviour for Positive / Neutral / Negative / Highly Negative.
#     """
#     if sentiment == "Positive":
#         return (
#             "Thank you so much for your positive review! We're really glad you are enjoying the app. "
#             "Your support motivates us to keep improving.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Neutral":
#         return (
#             "Thank you for taking the time to leave a review. "
#             "If you have any specific suggestions on how we can improve the app, "
#             "we’d love to hear them.\n\n"
#             f"Review: {review}"
#         )

#     if sentiment == "Highly Negative":
#         return (
#             "We're really sorry to hear about your experience. "
#             "It sounds like you faced a serious issue. "
#             "Please share more details (device, app version, and what exactly went wrong) so we can investigate and fix this as soon as possible. "
#             "You can also reach out to our support team directly from the app settings.\n\n"
#             f"Review: {review}"
#         )

#     # Default for 'Negative' and anything else
#     return (
#         "We're sorry that you had a negative experience with the app. "
#         "Thank you for pointing this out. If you can share a bit more information about the issue "
#         "(what you were doing when it happened, any error messages, etc.), "
#         "it will help us understand the problem and improve future versions.\n\n"
#         f"Review: {review}"
#     )


# def generate_reply(review: str, sentiment: str) -> str:
#     """
#     Generate a polite reply using Groq (LLaMA) if possible,
#     otherwise use a simple category-aware template.

#     LLM is instructed to reply in the SAME LANGUAGE as the review
#     and avoid sounding generic.
#     """
#     # If no Groq key, fall back to templates
#     if client is None:
#         return _template_reply(review, sentiment)

#     # Different tone instructions depending on sentiment
#     if sentiment == "Positive":
#         style_instruction = (
#             "Be warm and thankful. Mention at least one aspect they might be enjoying "
#             "and encourage them to keep using the app."
#         )
#     elif sentiment == "Neutral":
#         style_instruction = (
#             "Be appreciative but curious. Thank them and invite them to share concrete suggestions "
#             "so the developers can improve the app. Sound open to feedback."
#         )
#     elif sentiment == "Highly Negative":
#         style_instruction = (
#             "Be very apologetic, calm, and solution-focused. Assume they are frustrated. "
#             "Acknowledge the seriousness of their problem, apologize clearly, and ask for key details "
#             "like device, app version, and steps to reproduce. Emphasize that this feedback will be passed "
#             "to the development team."
#         )
#     else:  # Negative
#         style_instruction = (
#             "Be apologetic and constructive. Acknowledge their frustration, apologize, and ask for a bit more detail "
#             "so developers can understand and fix the issue in future updates."
#         )

#     try:
#         prompt = (
#             "You are an app developer or support agent responding to user reviews on an app store.\n\n"
#             f"User review (in original language): {review}\n"
#             f"Detected sentiment category: {sentiment}\n\n"
#             f"Response style: {style_instruction}\n\n"
#             "Very important instructions:\n"
#             "- First, automatically detect the language of the review.\n"
#             "- Reply in the SAME LANGUAGE as the review (if the review is in Hindi, reply in Hindi; if German, reply in German; etc.).\n"
#             "- Refer to the specific problem or praise mentioned in the review (for example, billing, crashes, subscription, brightness, etc.).\n"
#             "- Do NOT use the exact same sentence beginnings in every reply. Vary your opening sentence.\n"
#             "- Keep the reply short: 2–4 sentences.\n"
#             "- Focus on improving user experience and encourage the user to share any extra details that help developers.\n"
#             "- Do NOT invent technical details; keep it generic but empathetic.\n"
#         )

#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",  # good general-purpose model for replies
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=220,
#         )
#         content = completion.choices[0].message.content.strip()
#         print("GROQ REPLY OK")  # DEBUG
#         return content
#     except Exception as e:
#         print("GROQ reply error:", repr(e))
#         return _template_reply(review, sentiment)



# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# def _template_reply(review: str, sentiment: str) -> str:
#     if sentiment == "Positive":
#         return f"Thank you for your positive feedback! We're glad you're enjoying the app.\n\nReview: {review}"

#     if sentiment == "Neutral":
#         return f"Thank you for sharing your thoughts. If you have any suggestions, we'd love to hear them.\n\nReview: {review}"

#     if sentiment == "Highly Negative":
#         return (
#             "We're very sorry to hear about your experience. It sounds like a serious issue, "
#             "and we want to fix it quickly. Please share your device details and what exactly went wrong.\n\n"
#             f"Review: {review}"
#         )

#     # Negative
#     return (
#         "We're sorry you faced an issue while using the app. "
#         "Please share a few more details so we can understand and improve.\n\n"
#         f"Review: {review}"
#     )


# def generate_reply(review: str, sentiment: str) -> str:
#     if client is None or not GROQ_API_KEY:
#         return _template_reply(review, sentiment)

#     # Tone based on sentiment
#     if sentiment == "Positive":
#         tone = "warm, appreciative, friendly"
#     elif sentiment == "Neutral":
#         tone = "curious, polite, open to feedback"
#     elif sentiment == "Highly Negative":
#         tone = "apologetic, serious, calm, solution-focused"
#     else:
#         tone = "apologetic, understanding, constructive"

#     prompt = f"""
# You are an app support agent replying to a user review.

# REVIEW (detect language and reply in that same language):
# \"\"\"{review}\"\"\"

# SENTIMENT: {sentiment}

# REPLY INSTRUCTIONS:
# - Detect the review's language and reply **only** in that language.
# - DO NOT explain your detection process.
# - DO NOT talk about the task or steps.
# - DO NOT give examples.
# - DO NOT translate anything for the user.
# - DO NOT include the word "detected" or "language".
# - DO NOT add "---" or any formatting.
# - Reply naturally and directly to the user.
# - Keep it short: 2–3 sentences.
# - Address the specific issue (e.g., billing, login, crashing, performance, brightness).
# - Tone should be: {tone}

# Now write the reply:
# """

#     try:
#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",  
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=150,
#         )
#         reply_text = completion.choices[0].message.content.strip()
#         print("GROQ REPLY OK")
#         return reply_text
#     except Exception as e:
#         print("GROQ reply error:", repr(e))
#         return _template_reply(review, sentiment)



import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _template_reply(review: str, sentiment: str, lang_code: str = "en") -> str:
    # Very simple language-aware templates (English only for now, others will still get English fallback)
    if sentiment == "Positive":
        return f"Thank you for your positive feedback! We're glad you're enjoying the app.\n\nReview: {review}"

    if sentiment == "Neutral":
        return f"Thank you for sharing your thoughts. If you have any suggestions, we'd love to hear them.\n\nReview: {review}"

    if sentiment == "Highly Negative":
        return (
            "We're very sorry to hear about your experience. It sounds like a serious issue, "
            "and we want to fix it quickly. Please share your device details and what exactly went wrong.\n\n"
            f"Review: {review}"
        )

    # Negative
    return (
        "We're sorry you faced an issue while using the app. "
        "Please share a few more details so we can understand and improve.\n\n"
        f"Review: {review}"
    )


def generate_reply(review: str, sentiment: str, lang_code: str = "en") -> str:
    """
    Generate a polite reply using Groq.
    lang_code comes from the UI (e.g., 'en', 'de', 'hi').
    We DO NOT auto-detect language anymore.
    """
    if client is None or not GROQ_API_KEY:
        return _template_reply(review, sentiment, lang_code)

    # Tone based on sentiment
    if sentiment == "Positive":
        tone = "warm, appreciative, friendly"
    elif sentiment == "Neutral":
        tone = "curious, polite, open to feedback"
    elif sentiment == "Highly Negative":
        tone = "apologetic, serious, calm, solution-focused"
    else:
        tone = "apologetic, understanding, constructive"

    prompt = f"""
You are an app support agent replying to a user review.

REVIEW:
\"\"\"{review}\"\"\"

SENTIMENT: {sentiment}

LANGUAGE REQUIREMENT:
- Reply ONLY in the language corresponding to this code: "{lang_code}".
- If the review is in another language, IGNORE that and still reply in the language for "{lang_code}".
- Do NOT mention the language code or talk about language detection.

STYLE INSTRUCTIONS:
- Tone: {tone}
- Length: 2–3 sentences.
- Address the specific issue (e.g., billing, subscription, bugs, performance, brightness).
- Do NOT explain your reasoning.
- Do NOT show examples.
- Do NOT translate anything or add extra explanations.
Just write the final reply text.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        reply_text = completion.choices[0].message.content.strip()
        print("GROQ REPLY OK")
        return reply_text
    except Exception as e:
        print("GROQ reply error:", repr(e))
        return _template_reply(review, sentiment, lang_code)
