from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__)

model = joblib.load(MODEL_DIR / "logreg_model.joblib")
scaler = joblib.load(MODEL_DIR / "scaler.joblib")
feature_columns = joblib.load(MODEL_DIR / "feature_columns.joblib")

NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges", "TotalServices"]
BINARY_COLS = [
    "SeniorCitizen", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "PaperlessBilling",
]
CATEGORICAL_COLS = ["gender", "InternetService", "Contract", "PaymentMethod"]
SERVICE_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]
REQUIRED_FIELDS = (
    ["tenure", "MonthlyCharges", "TotalCharges"] + BINARY_COLS + CATEGORICAL_COLS
)
THRESHOLD = 0.3

def tenure_group(t):
    if t <= 12:
        return "0-1yr"
    elif t <= 24:
        return "1-2yr"
    elif t <= 48:
        return "2-4yr"
    return "4yr+"

def preprocess(payload: dict) -> pd.DataFrame:
    df = pd.DataFrame([payload])
    df["TenureGroup"] = df["tenure"].apply(tenure_group)
    df["TotalServices"] = (df[SERVICE_COLS] == "Yes").sum(axis=1)
    for col in BINARY_COLS:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS + ["TenureGroup"])
    df = df.reindex(columns=feature_columns, fill_value=0)
    df[NUMERIC_COLS] = scaler.transform(df[NUMERIC_COLS])
    return df

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    try:
        X = preprocess(payload)
        proba = float(model.predict_proba(X)[0, 1])
    except Exception as exc:
        return jsonify({"error": f"Could not process input: {exc}"}), 400

    return jsonify({
        "churn_probability": round(proba, 4),
        "churn_prediction": int(proba >= THRESHOLD),
        "threshold": THRESHOLD,
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)