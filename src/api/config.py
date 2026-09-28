from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"

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