
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