# 📱AI-Powered Multilingual Review Analysis System

A Streamlit-based web application that fetches app reviews from Google Play,
performs multilingual sentiment analysis, and generates polite AI-based replies
to user reviews.

## 🚀 Features
- Fetch reviews from Google Play using app name
- Multilingual sentiment analysis (English, Hindi, German, etc.)
- Sentiment categories: Positive, Neutral, Negative, Highly Negative
- AI-generated replies in a language you choose, independent of the review language
- Manual review input option
- Download replies as a text file

## 🛠 Tech Stack
- Python
- Streamlit
- NLP
- Groq (LLaMA) for sentiment + replies, with a TextBlob/template offline fallback
- Google Play Scraper

## ▶️ Run Locally

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your GROQ_API_KEY
streamlit run app.py
```

### Configuration

`GROQ_API_KEY` is the only key required — it powers both sentiment analysis and
reply generation. Without it the app still runs, falling back to TextBlob
scoring and static English reply templates, and the UI will tell you when that
happens.

## 🌐 Live Demo
https://app-review-assistant-etwwrdzitudxlpjpdcfjd6.streamlit.app

## 🧪 How to Test
- Google Play mode: try "Netflix", 10–20 reviews
- Manual mode: paste mixed-language reviews
- Change the reply language and generate replies

```bash
python -m pytest tests/ -v
```
