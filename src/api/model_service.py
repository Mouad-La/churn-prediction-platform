import joblib
import numpy as np

from src.api.config import MODEL_DIR, THRESHOLD
from src.api.preprocessing import preprocess


class ChurnService:
    def __init__(self):
        self.model = joblib.load(MODEL_DIR / "logreg_model.joblib")
        self.scaler = joblib.load(MODEL_DIR / "scaler.joblib")
        self.columns = joblib.load(MODEL_DIR / "feature_columns.joblib")

    def _proba(self, X) -> float:
        return float(self.model.predict_proba(X)[0, 1])

    def predict(self, payload: dict) -> dict:
        X = preprocess(payload, self.scaler, self.columns)
        proba = self._proba(X)
        return {
            "churn_probability": round(proba, 4),
            "churn_prediction": int(proba >= THRESHOLD),
            "threshold": THRESHOLD,
        }

    def explain(self, payload: dict, top_n: int = 5) -> dict:
        X = preprocess(payload, self.scaler, self.columns)
        contributions = X.iloc[0].values * self.model.coef_[0]
        order = np.argsort(np.abs(contributions))[::-1][:top_n]
        drivers = [
            {
                "feature": self.columns[i],
                "contribution": round(float(contributions[i]), 4),
                "direction": "increases churn risk"
                if contributions[i] > 0 else "decreases churn risk",
            }
            for i in order
        ]
        return {
            **self.predict(payload),
            "top_drivers": drivers,
            "method": "coefficient-based contributions (log-odds)",
        }