# Customer Churn Prediction & Business Analytics Platform

An end-to-end machine learning system that predicts telecom customer churn,
explains individual predictions, and serves them through a REST API —
built to mirror how a data science team would ship this inside a consulting
or product organization.

## Business Problem

Acquiring a new customer typically costs 5–25x more than retaining an
existing one. In this dataset, 26.5% of customers churned — nearly 1 in 4.
Rather than only measuring churn after the fact, this project predicts it
in advance, when the business can still intervene.

Two findings drove the modeling and business recommendations:
- **Contract type dominates.** Month-to-month customers churn far more than
  one- or two-year contract holders — the single strongest signal in every
  model tested.
- **Risk is concentrated early.** Churned customers have a lower median
  tenure than retained customers — new customers are the highest-risk group,
  not long-tenured ones.

## Architecture

Telco Customer CSV (Kaggle)
│
▼
Python cleaning & feature engineering (Pandas)
│
▼
PostgreSQL (normalized customers / subscriptions schema, FK + indexes)
│
▼
Model training & comparison
(Logistic Regression, Random Forest, XGBoost — scikit-learn, XGBoost)
│
▼
SHAP explainability (global) + coefficient-based explanations (per-request)
│
▼
Flask REST API (/health, /predict, /explain)
│
▼
Docker Compose (API + PostgreSQL, gunicorn)


## Key Results

| Model | Accuracy | Precision (churn) | Recall (churn) | F1 (churn) | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.80 | 0.65 | 0.52 | 0.58 | 0.8425 |
| Random Forest | 0.79 | 0.63 | 0.50 | 0.56 | 0.8233 |
| XGBoost (untuned) | 0.80 | 0.64 | 0.54 | 0.59 | 0.8405 |
| XGBoost (tuned, GridSearchCV) | 0.79 | 0.63 | 0.53 | 0.57 | 0.8337 |

**Logistic Regression was selected as the primary model** — it matched or
beat the tree-based models on this dataset while remaining fully
interpretable via coefficients. Tuning did not meaningfully improve
XGBoost, which suggests the bottleneck was signal in the data rather
than model capacity.

**Threshold tuning mattered more than model choice or tuning.** At the
default 0.5 cutoff, Logistic Regression recall was 0.52. Lowering the
decision threshold to **0.3** raised recall to **0.76** (precision 0.53),
catching substantially more at-risk customers at the cost of more false
positives — a tradeoff the business should set based on retention-offer
cost vs. cost of losing a customer.

## Explainability

- **Global:** SHAP (`TreeExplainer` on XGBoost) confirms tenure, contract
  type, and fiber-optic internet service as the top drivers, consistent
  with both the Logistic Regression coefficients and the original EDA.
- **Per-prediction:** the `/explain` endpoint returns each feature's
  coefficient-based contribution (log-odds) for a single customer. This is
  not a full SHAP computation — see Limitations.

## Project Structure

churn-prediction-platform/
├── data/
│ ├── raw/ # original Kaggle CSV (not committed)
│ └── processed/ # cleaned + feature-engineered CSVs
├── notebooks/ # exploratory work (cleaning, EDA, stats, modeling)
├── src/
│ └── api/
│ ├── app.py # Flask routes
│ ├── config.py # constants, paths, threshold
│ ├── preprocessing.py # feature engineering shared by API + notebooks
│ └── model_service.py # model loading, predict, explain
├── models/ # saved model, scaler, feature columns (.joblib)
├── tests/ # pytest suite for the API and preprocessing
├── Dockerfile
├── docker-compose.yml
├── requirements.txt # full dev environment
├── requirements-api.txt # minimal, pinned, used by the Docker image
└── README.md


## How to Run

### Option A — Docker (recommended)

```bash
git clone <your-repo-url>
cd churn-prediction-platform
cp .env.example .env        # set DB_PASSWORD
docker compose up --build
```

API available at `http://127.0.0.1:5000`.

### Option B — Local development

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m src.api.app
```

### Dataset

The raw CSV is not committed (see Limitations). Download the
[Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
from Kaggle and place it at `data/raw/telco_churn_raw.csv`, then run the
notebooks in order (`01` through `06`) to reproduce cleaning, EDA, and the
saved model artifacts.

## API Reference

### `GET /health`
Returns `{"status": "ok"}`.

### `POST /predict`
Body: raw customer fields (see `sample.json` for a full example).

```json
{
  "churn_probability": 0.6993,
  "churn_prediction": 1,
  "threshold": 0.3
}
```

### `POST /explain`
Same body as `/predict`. Adds the top contributing features:

```json
{
  "churn_probability": 0.6993,
  "churn_prediction": 1,
  "threshold": 0.3,
  "method": "coefficient-based contributions (log-odds)",
  "top_drivers": [
    {"feature": "tenure", "contribution": 1.4429, "direction": "increases churn risk"},
    {"feature": "InternetService_Fiber optic", "contribution": 1.0423, "direction": "increases churn risk"}
  ]
}
```

## Testing

```bash
python -m pytest -v
```

11 tests covering health, predict (high/low risk), validation errors, and
`tenure_group` boundary conditions.

## Limitations & Next Steps

- The 0.3 decision threshold was selected by evaluating candidate
  thresholds on the held-out test set, not a separate validation set —
  a mild form of leakage into model selection worth fixing with a proper
  train/validation/test split.
- `/explain` returns coefficient-based log-odds contributions, not true
  SHAP values. They agree closely for scaled numeric features but are not
  mean-centered for binary/dummy features. Full SHAP (via `TreeExplainer`
  on XGBoost) is used only in the offline analysis, not served live.
- The Docker Compose `db` service is provisioned but not yet loaded with
  data or used by the API; the API currently only depends on the saved
  model artifacts.
- The raw dataset is not committed to the repository (see the
  `data/raw` note above); the Kaggle license and Git's poor handling of
  data files were the deciding factors — see the project write-up for
  the full reasoning.
- No frontend dashboard yet. A React + Plotly dashboard and a Power BI
  executive report are planned to both consume this API.
- No CI pipeline (GitHub Actions) yet running the test suite on push.