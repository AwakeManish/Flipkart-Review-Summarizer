import json
import os
import pandas as pd
from glob import glob
import re

def extract_number(text):
    return int(re.search(r'\d+', text).group())

def extract_mp(camera_str):
    matches = re.findall(r'(\d+)', camera_str)
    return sum(map(int, matches)) if matches else 0

def analyze_successful_products():
    files = glob("data/raw/*.json")
    rows = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        specs = data['metadata']['normalized_specs']
        rating = float(data['metadata'].get("rating", 0))

        if rating >= 4.1:  # successful product
            rows.append({
                "price": int(data['metadata']['price']),
                "battery_capacity": extract_number(specs["battery_capacity"]),
                "camera_mp": extract_mp(specs["camera"]),
                "ram": extract_number(specs["ram"]),
                "storage": extract_number(specs["storage"]),
                "processor_type": specs["processor_type"]
            })

    df = pd.DataFrame(rows)
    df.to_csv("data/successful_products_stats.csv", index=False)

    # Show statistical summary
    print("=== Successful Product Averages ===")
    print(df.describe())
    print("\n=== Most Common Processors ===")
    print(df["processor_type"].value_counts())

if __name__ == "__main__":
    analyze_successful_products()
