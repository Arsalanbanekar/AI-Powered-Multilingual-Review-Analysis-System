# 📱 App Review Assistant (AI-Powered)

A Streamlit-based web application that fetches app reviews from Google Play,
performs multilingual sentiment analysis, and generates polite AI-based replies
to user reviews.

## 🚀 Features
- Fetch reviews from Google Play using app name
- Multilingual sentiment analysis (English, Hindi, German, etc.)
- Sentiment categories: Positive, Neutral, Negative, Highly Negative
- AI-generated responses in the same language as the review
- Manual review input option
- Download replies as a text file

## 🛠 Tech Stack
- Python
- Streamlit
- NLP
- Rule-based + LLM-based sentiment analysis
- Google Play Scraper
- Groq / OpenAI (optional)

## ▶️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py



## 🌐 Live Demo
https://app-review-assistant-arsalanbanekar.streamlit.app

## 🧪 How to Test
- Google Play mode: try “Netflix”, 10–20 reviews
- Manual mode: paste mixed-language reviews
- Change reply language and generate replies
