import pandas as pd
import os
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_FILE = "data/processed/reviews_with_sentiment.csv"
OUTPUT_FILE = "data/processed/aspect_sentiment_summary.csv"

ASPECTS = {
    "Design": ["Build Quality", "Material", "Color Options", "Ergonomics", "Weight", "Aesthetics"],
    "Display": ["Size", "Resolution", "Brightness", "Refresh Rate", "Color Accuracy", "Touch Responsiveness"],
    "Performance": ["Processor", "RAM", "Speed", "Thermal Management", "Gaming Performance"],
    "Battery": ["Battery Life", "Charging Speed", "Charging Technology", "Battery Capacity"],
    "Camera": {
        "Rear Camera": ["Photo Quality", "Video Quality", "Low Light Performance", "Stabilization", "Zoom Capabilities"],
        "Front Camera": ["Selfie Quality", "Video Call Performance", "Portrait Mode"]
    },
    "Software": ["Operating System", "OS Updates", "UI/UX", "Bloatware", "Customization Options"],
    "Audio": ["Speaker Quality", "Earphone Output", "Microphone Quality", "Dolby or Surround Sound"],
    "Connectivity": ["5G/4G Support", "Wi-Fi", "Bluetooth", "NFC", "Dual SIM", "Call Quality"],
    "Storage": ["Internal Storage", "Expandable Storage", "Storage Speed"],
    "Value for Money": [],
    "Durability": [],
    "Heating Issues": [],
    "Face Unlock / Fingerprint": ["Accuracy", "Speed", "Placement"],
    "Accessories": ["Charger Included", "Case in the Box", "Screen Protector", "Earphones"],
    "Brand Reputation": []
}

analyzer = SentimentIntensityAnalyzer()

def clean_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def flatten_aspects(aspects_dict):
    flat_list = []
    for category, sub in aspects_dict.items():
        if isinstance(sub, list):
            for sub_item in sub:
                flat_list.append((category, sub_item.lower()))
        elif isinstance(sub, dict):
            for subcat, items in sub.items():
                for item in items:
                    flat_list.append((category, item.lower()))
        else:
            flat_list.append((category, str(sub).lower()))
    return flat_list

flattened_aspects = flatten_aspects(ASPECTS)

def extract_aspect_sentiments(df):
    aspect_data = []

    for _, row in df.iterrows():
        review = clean_text(row["review"])
        sentences = re.split(r"[.!?]", review)

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            for category, keyword in flattened_aspects:
                if keyword in sent:
                    score = analyzer.polarity_scores(sent)["compound"]
                    sentiment = (
                        "Positive" if score > 0.05
                        else "Negative" if score < -0.05
                        else "Neutral"
                    )
                    aspect_data.append({
                        "title": row["title"],
                        "aspect_category": category,
                        "aspect_term": keyword,
                        "sentence": sent,
                        "score": score,
                        "sentiment": sentiment
                    })

    return pd.DataFrame(aspect_data)

def summarize_aspect_opinions(aspect_df):
    summary = aspect_df.groupby(["title", "aspect_category"]).agg(
        avg_score=("score", "mean"),
        positive_pct=("sentiment", lambda x: (x == "Positive").mean() * 100),
        negative_pct=("sentiment", lambda x: (x == "Negative").mean() * 100),
        neutral_pct=("sentiment", lambda x: (x == "Neutral").mean() * 100),
        mentions=("sentiment", "count")
    ).reset_index()
    return summary

def main():
    os.makedirs("data/processed", exist_ok=True)

    df = pd.read_csv(INPUT_FILE)
    aspect_df = extract_aspect_sentiments(df)

    aspect_df.to_csv("data/processed/aspect_level_reviews.csv", index=False)
    print("✅ Extracted aspect-based opinions → aspect_level_reviews.csv")

    summary = summarize_aspect_opinions(aspect_df)
    summary.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Summary saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
