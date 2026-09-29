# Customer Churn Prediction & Business Analytics Platform

An end-to-end machine learning system that predicts telecom customer churn,
explains individual predictions, and serves them through a REST API and two
dashboards — built to mirror how a data science team would ship this inside
a consulting or product organization.

## Business Problem

Acquiring a new customer typically costs 5–25x more than retaining an
existing one. In this dataset, 26.5% of customers churned — nearly 1 in 4.
Rather than only measuring churn after the fact, this project predicts it
in advance, when the business can still intervene.

Two findings drove the modeling and business recommendations:
- **Contract type dominates.** Month-to-month customers churn at 42.7%,
  versus 11.3% for one-year and 2.8% for two-year contracts — roughly a
  15x gap between the highest- and lowest-risk contract types. This is the
  single strongest signal in every model tested and the top feature by
  SHAP importance.
- **Risk is concentrated early.** Tenure is bimodal — a cluster of very new
  customers and a separate cluster of long-tenured ones. Churned customers
  have a lower median tenure than retained customers: new customers are the
  highest-risk group, not long-tenured ones.

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
Flask REST API (/health, /predict, /explain) — validated input, CORS-enabled
│
┌────┴────┐
▼ ▼
React dashboard Power BI report
(operational, (executive,
per-customer, aggregate view,
calls the API) reads PostgreSQL directly)
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

**Logistic Regression was selected as the primary model.** It matched or
beat the tree-based models on this dataset while remaining fully
interpretable via coefficients. Hyperparameter tuning did not meaningfully
improve XGBoost, suggesting the bottleneck was signal in the data rather
than model capacity — all three algorithms converged to a similar
performance ceiling (ROC-AUC 0.82–0.84), which is itself informative.

**Threshold tuning mattered more than model choice.** At the default 0.5
cutoff, Logistic Regression recall on the churn class was 0.52. Lowering
the decision threshold to **0.3** raised recall to **0.76** (precision
0.53) — catching substantially more at-risk customers at the cost of more
false positives. This threshold was selected by evaluating candidates on
the held-out test set (see Limitations) and should ultimately be set based
on the business's retention-offer cost versus the cost of losing a customer.

## Explainability

- **Global:** SHAP (`TreeExplainer` on XGBoost) confirms tenure, contract
  type, and fiber-optic internet service as the top drivers, consistent
  with both the Logistic Regression coefficients and the original EDA.
- **Per-prediction:** the `/explain` endpoint returns each feature's
  coefficient-based contribution (log-odds) for a single customer. This is
  not a full SHAP computation — see Limitations.

## Dashboards

Two dashboards were built deliberately for two different audiences and
questions, both reading from the same underlying pipeline:

- **React operational dashboard** (`dashboard-react/`): answers "what's
  the risk for this one customer, right now?" A form posts a customer's
  raw attributes to `/explain` and displays the churn probability,
  decision, and top contributing factors. This is the tool a retention
  agent would use during a live customer interaction.
- **Power BI executive report** (`powerbi/churn_dashboard.pbix`): answers
  "what's the overall shape of churn across our customer base, and where
  should we focus?" It shows overall churn rate, churn rate by contract
  type, and the tenure distribution, with a contract-type slicer for
  interactive filtering. This is the tool a manager would use in a
  quarterly review.

Power BI connects **directly to PostgreSQL**, not through the Flask API —
a deliberate choice, since BI tools are built for direct data connections
and Import mode is simpler and faster than round-tripping through an
application API for a dataset this size.

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
│ ├── preprocessing.py # feature engineering + validation, shared by API + notebooks
│ └── model_service.py # model loading, predict, explain
├── models/ # saved model, scaler, feature columns (.joblib)
├── tests/ # pytest suite for the API and preprocessing
├── dashboard-react/ # React + Vite operational dashboard
├── powerbi/
│ └── churn_dashboard.pbix # executive report
├── Dockerfile
├── docker-compose.yml
├── requirements.txt # full dev environment
├── requirements-api.txt # minimal, pinned, used by the Docker image
└── README.md

## How to Run

### Backend — Docker (recommended)

```bash
git clone <your-repo-url>
cd churn-prediction-platform
cp .env.example .env        # set DB_PASSWORD
docker compose up --build
```

API available at `http://127.0.0.1:5000`.

### Backend — local development

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m src.api.app
```

### React dashboard

```bash
cd dashboard-react
npm install
npm run dev
```

Opens at `http://localhost:5173`. Requires the Flask API running (locally
or via Docker) on port 5000.

### Power BI dashboard

Open `powerbi/churn_dashboard.pbix` in Power BI Desktop. It connects to a
local PostgreSQL instance at `localhost:5432`, database `churn_db` — see
Limitations for why this differs from the Docker Compose database.

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
Body: raw customer fields (see `sample.json` for a full example). Returns
400 with a list of specific validation errors for missing fields, invalid
types, out-of-range numeric values, or unrecognized category values.

```json
{
  "churn_probability": 0.6993,
  "churn_prediction": 1,
  "threshold": 0.3
}
```

### `POST /explain`
Same body and validation as `/predict`. Adds the top contributing features:

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

13 tests covering health, predict (high/low risk), missing-field and
invalid-JSON errors, out-of-range and invalid-category validation, and
`tenure_group` boundary conditions.

## Limitations & Next Steps

- **Threshold selection used the test set.** The 0.3 decision threshold
  was chosen by evaluating candidate thresholds directly on the held-out
  test set rather than a separate validation set — a mild form of leakage
  into model selection. A proper train/validation/test split would fix
  this.
- **`/explain` is not true SHAP.** It returns coefficient-based log-odds
  contributions for the Logistic Regression model. These closely match
  SHAP values for scaled numeric features but are not mean-centered for
  binary/dummy features, so they diverge from true Shapley values by a
  constant offset per feature. Full SHAP (via `TreeExplainer` on XGBoost)
  is used only in the offline analysis (Step 9), not served live.
- **The Docker Compose `db` service is provisioned but unused.** The API
  currently depends only on the saved model artifacts, not the database.
  Power BI reads from a separate, locally-installed PostgreSQL instance
  (port 5432) rather than the containerized one (port 5433) — the two are
  not currently the same database, and only the local instance has data
  loaded. Consolidating onto one database is a natural next step.
- **The raw dataset is not committed to the repository.** The Kaggle
  license and Git's poor handling of data files were the deciding factors.
- **No CI pipeline yet.** Tests run locally via `pytest`; a GitHub Actions
  workflow to run them automatically on push is a natural next step.
- **No cloud deployment.** The project runs locally via Docker Compose.
  AWS (or similar) deployment was scoped out to keep the project complete
  and polished rather than rushed.
- **CORS is fully open (`CORS(app)`) for local development.** A production
  deployment should restrict allowed origins to the actual frontend domain.