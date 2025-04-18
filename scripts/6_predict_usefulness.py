

import pandas as pd
import joblib
import re

# Load model and encoders
model = joblib.load("model/usefulness_predictor.pkl")
encoders = joblib.load("model/encoders.pkl")
stats_df = pd.read_csv("data/successful_products_stats.csv")

# Calculate averages from successful products
avg_stats = stats_df.mean(numeric_only=True)
common_processors = stats_df["processor_type"].value_counts().head(3).index.tolist()

# Input product to evaluate
product = {
    "price": "10000",
    "battery_capacity": "5000 mAh",
    "display_type": "PLS LCD",
    "camera": "54MP + 2MP",
    "network_type": "5G, 4G, 3G, 2G",
    "ram": "8 GB",
    "storage": "128 GB",
    "processor_type": "Dimensity 6300"
}

# Helper functions
def extract_number(val):
    match = re.search(r'\d+', val)
    return int(match.group()) if match else 0

def extract_mp(camera):
    return sum(map(int, re.findall(r'\d+', camera)))

# Create feature set for prediction
features = {
    "price": int(product["price"]),
    "battery_capacity": extract_number(product["battery_capacity"]),
    "display_type": product["display_type"],
    "camera_mp": extract_mp(product["camera"]),
    "network_type": len(product["network_type"].split(',')),
    "ram": extract_number(product["ram"]),
    "storage": extract_number(product["storage"]),
    "processor_type": product["processor_type"]
}

# Encode categorical features
for col in ["display_type", "processor_type"]:
    if features[col] in encoders[col].classes_:
        features[col] = encoders[col].transform([features[col]])[0]
    else:
        features[col] = -1  # unknown category

# Predict usefulness
df = pd.DataFrame([features])
prediction = model.predict(df)[0]

# Prepare improvement suggestions
suggestions = []

if features["ram"] < avg_stats["ram"]:
    suggestions.append(f"Increase RAM to at least {int(avg_stats['ram'])} GB.")

if features["battery_capacity"] < avg_stats["battery_capacity"]:
    suggestions.append(f"Increase battery to around {int(avg_stats['battery_capacity'])} mAh.")

if features["camera_mp"] < avg_stats["camera_mp"]:
    suggestions.append(f"Improve camera (total MP > {int(avg_stats['camera_mp'])}).")

if product["processor_type"] not in common_processors:
    suggestions.append(f"Use a more popular processor like {common_processors[0]}.")

# Price-based recommendation using similar specs
similar = stats_df[
    (stats_df["ram"] >= features["ram"]) &
    (stats_df["battery_capacity"] >= features["battery_capacity"]) &
    (stats_df["camera_mp"] >= features["camera_mp"])
]

if not similar.empty and features["price"] > similar["price"].mean():
    avg_similar_price = int(similar["price"].mean())
    suggestions.append(f"Consider lowering price to around ₹{avg_similar_price} to stay competitive.")

# Final output
summary = {
    "useful_to_sell": bool(prediction),
    "suggestions": suggestions
}

print(summary)
