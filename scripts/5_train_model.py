import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv("data/processed_products.csv")

# Encode categorical features
encoders = {}
for col in ["display_type", "processor_type"]:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

X = df.drop(columns=["useful_to_sell"])
y = df["useful_to_sell"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "model/usefulness_predictor.pkl")
joblib.dump(encoders, "model/encoders.pkl")

print("✅ Model training complete!")
