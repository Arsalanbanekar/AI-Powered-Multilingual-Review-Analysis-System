import os
from datetime import datetime
from typing import List

def save_replies_to_txt(
    label: str,
    reviews: List[str],
    sentiments: List[str],
    scores: List[float],
    replies: List[str],
) -> str:
    """Save reviews, sentiments, scores, and replies into a formatted .txt file."""

    # Create folder safely
    os.makedirs("downloads", exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_label = "".join(c for c in label if c.isalnum() or c in ("-", "_")) or "app"
    path = f"downloads/{safe_label}_reviews_{timestamp}.txt"

    with open(path, "w", encoding="utf-8") as f:
        for i, (r, s, sc, rep) in enumerate(zip(reviews, sentiments, scores, replies), start=1):
            f.write(f"Review {i}:\n")
            f.write(r + "\n\n")
            f.write(f"Sentiment: {s} (score={sc:.3f})\n\n")
            f.write("Reply:\n")
            f.write(rep + "\n")
            f.write("-" * 60 + "\n\n")

    return path
