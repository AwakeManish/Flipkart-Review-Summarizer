import os
import json
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

RAW_DIR = "data/raw"
OUTPUT_FILE = "data/processed/labeled_reviews.csv"

analyzer = SentimentIntensityAnalyzer()

def score_sentiment(reviews):
    scores = [analyzer.polarity_scores(review)["compound"] for review in reviews]
    avg_score = sum(scores) / len(scores)
    return avg_score

def check_useful_specs(specs: dict):
    keywords = {
        "5G": False,
        "battery": False,
        "display": False,
        "camera": False
    }

    spec_text = " ".join([f"{k}: {v}" for k, v in specs.items()]).lower()

    if "5g" in spec_text:
        keywords["5G"] = True
    if "5000mah" in spec_text or "4500mah" in spec_text:
        keywords["battery"] = True
    if "amoled" in spec_text or "ips" in spec_text:
        keywords["display"] = True
    if "camera" in spec_text and ("50mp" in spec_text or "64mp" in spec_text or "108mp" in spec_text):
        keywords["camera"] = True

    return sum(keywords.values()), keywords

def process_products():
    all_data = []

    for filename in os.listdir(RAW_DIR):
        filepath = os.path.join(RAW_DIR, filename)
        if filename.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                product = json.load(f)

                metadata = product.get("metadata", {})
                reviews = product.get("reviews", [])

                if len(reviews) < 2:
                    continue  # Skip products with too few reviews

                meta = {
                    "title": metadata.get("title"),
                    "price": metadata.get("price"),
                    "brand": metadata.get("brand"),
                    "rating": metadata.get("rating"),
                    "normalized_specs": metadata.get("normalized_specs", {})
                }

                for review in reviews:
                    all_data.append({
                        **meta,
                        "review": review
                    })

    return pd.DataFrame(all_data)


def main():
    os.makedirs("data/processed", exist_ok=True)
    df = process_products()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Semi-annotated dataset saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
