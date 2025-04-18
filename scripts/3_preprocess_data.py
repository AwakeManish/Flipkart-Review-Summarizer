import json
import os
import pandas as pd
from glob import glob
import re

def extract_mp(camera_str):
    matches = re.findall(r'(\d+)', camera_str)
    return sum(map(int, matches)) if matches else 0

def extract_number(spec):
    return int(re.search(r'\d+', spec).group())

def clean_record(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    specs = data['metadata']['normalized_specs']
    return {
        "price": int(data['metadata']['price']),
        "battery_capacity": extract_number(specs['battery_capacity']),
        "display_type": specs['display_type'],
        "camera_mp": extract_mp(specs['camera']),
        "network_type": len(specs['network_type'].split(',')),
        "ram": extract_number(specs['ram']),
        "storage": extract_number(specs['storage']),
        "processor_type": specs['processor_type'],
        "useful_to_sell": 1 if float(data['metadata'].get("rating", 0)) >= 4.1 else 0
    }

def main():
    files = glob('data/raw/*.json')
    rows = [clean_record(file) for file in files]
    df = pd.DataFrame(rows)
    df.to_csv("data/processed_products.csv", index=False)
    print("✅ Data preprocessing complete!")

if __name__ == "__main__":
    main()
