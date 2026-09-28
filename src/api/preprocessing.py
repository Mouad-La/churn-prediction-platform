import pandas as pd

from src.api.config import (
    BINARY_COLS, CATEGORICAL_COLS, NUMERIC_COLS, SERVICE_COLS,
)

VALID_CATEGORIES = {
    "gender": {"Male", "Female"},
    "InternetService": {"Fiber optic", "DSL", "No"},
    "Contract": {"Month-to-month", "One year", "Two year"},
    "PaymentMethod": {
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)",
    },
}
YES_NO_COLS = BINARY_COLS  # SeniorCitizen..PaperlessBilling, already Yes/No
RAW_NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]


def validate_payload(payload: dict) -> list[str]:
    """Return a list of human-readable error messages. Empty list = valid."""
    errors = []

    for col in RAW_NUMERIC_COLS:
        value = payload.get(col)
        try:
            num = float(value)
        except (TypeError, ValueError):
            errors.append(f"'{col}' must be a number, got {value!r}")
            continue
        if num < 0:
            errors.append(f"'{col}' cannot be negative")
        if col == "tenure" and num > 100:
            errors.append("'tenure' must be 100 months or fewer")
        if col in ("MonthlyCharges", "TotalCharges") and num > 100000:
            errors.append(f"'{col}' is unrealistically large")

    for col in YES_NO_COLS:
        value = payload.get(col)
        if value not in ("Yes", "No"):
            errors.append(f"'{col}' must be 'Yes' or 'No', got {value!r}")

    for col, allowed in VALID_CATEGORIES.items():
        value = payload.get(col)
        if value not in allowed:
            errors.append(f"'{col}' must be one of {sorted(allowed)}, got {value!r}")

    return errors


def tenure_group(t):
    if t <= 12:
        return "0-1yr"
    elif t <= 24:
        return "1-2yr"
    elif t <= 48:
        return "2-4yr"
    return "4yr+"


def preprocess(payload: dict, scaler, feature_columns) -> pd.DataFrame:
    df = pd.DataFrame([payload])
    df[RAW_NUMERIC_COLS] = df[RAW_NUMERIC_COLS].astype(float)
    df["TenureGroup"] = df["tenure"].apply(tenure_group)
    df["TotalServices"] = (df[SERVICE_COLS] == "Yes").sum(axis=1)
    for col in BINARY_COLS:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS + ["TenureGroup"])
    df = df.reindex(columns=feature_columns, fill_value=0)
    df[NUMERIC_COLS] = scaler.transform(df[NUMERIC_COLS])
    return df