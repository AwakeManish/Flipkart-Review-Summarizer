import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_FILE = "data/processed/labeled_reviews.csv"
OUTPUT_FILE = "data/processed/reviews_with_sentiment.csv"
SUMMARY_FILE = "data/processed/product_sentiment_summary.csv"

analyzer = SentimentIntensityAnalyzer()

def get_sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def analyze_sentiment(df):
    sentiments = []
    for review in df["review"]:
        score = analyzer.polarity_scores(review)
        compound = score["compound"]
        sentiments.append({
            "compound": compound,
            "label": get_sentiment_label(compound)
        })

    sentiment_df = pd.DataFrame(sentiments)
    return pd.concat([df.reset_index(drop=True), sentiment_df], axis=1)

def summarize_by_product(df):
    summary = df.groupby("title").agg(
        avg_sentiment=("compound", "mean"),
        positive_pct=("label", lambda x: (x == "Positive").mean() * 100),
        negative_pct=("label", lambda x: (x == "Negative").mean() * 100),
        neutral_pct=("label", lambda x: (x == "Neutral").mean() * 100),
        total_reviews=("label", "count")
    ).reset_index()

    def classify_sentiment(row):
        if row["positive_pct"] > 60:
            return "Mostly Positive"
        elif row["negative_pct"] > 50:
            return "Mostly Negative"
        else:
            return "Mixed"

    summary["overall_sentiment"] = summary.apply(classify_sentiment, axis=1)
    return summary

def main():
    df = pd.read_csv(INPUT_FILE)
    os.makedirs("data/processed", exist_ok=True)

    sentiment_df = analyze_sentiment(df)
    sentiment_df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Sentiment scores saved to {OUTPUT_FILE}")

    summary = summarize_by_product(sentiment_df)
    summary.to_csv(SUMMARY_FILE, index=False)
    print(f"✅ Product-level summary saved to {SUMMARY_FILE}")

if __name__ == "__main__":
    main()
