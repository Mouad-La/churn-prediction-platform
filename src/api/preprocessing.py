import pandas as pd

from src.api.config import (
    BINARY_COLS, CATEGORICAL_COLS, NUMERIC_COLS, SERVICE_COLS,
)


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
    df["TenureGroup"] = df["tenure"].apply(tenure_group)
    df["TotalServices"] = (df[SERVICE_COLS] == "Yes").sum(axis=1)
    for col in BINARY_COLS:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS + ["TenureGroup"])
    df = df.reindex(columns=feature_columns, fill_value=0)
    df[NUMERIC_COLS] = scaler.transform(df[NUMERIC_COLS])
    return df