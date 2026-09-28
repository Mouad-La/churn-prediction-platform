import json
from pathlib import Path

import pytest

from src.api.app import app
from src.api.preprocessing import tenure_group

SAMPLE_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def load(name):
    with open(SAMPLE_DIR / name) as f:
        return json.load(f)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_predict_high_risk(client):
    r = client.post("/predict", json=load("sample.json"))
    assert r.status_code == 200
    assert r.get_json()["churn_probability"] == pytest.approx(0.6993, abs=1e-3)
    assert r.get_json()["churn_prediction"] == 1


def test_predict_low_risk(client):
    r = client.post("/predict", json=load("sample_low.json"))
    assert r.status_code == 200
    assert r.get_json()["churn_prediction"] == 0


def test_missing_fields_returns_400(client):
    r = client.post("/predict", json={"tenure": 2})
    assert r.status_code == 400
    assert "MonthlyCharges" in r.get_json()["fields"]


def test_invalid_json_returns_400(client):
    r = client.post("/predict", data="not json", content_type="application/json")
    assert r.status_code == 400

def test_invalid_tenure_returns_400(client):
    payload = load("sample.json")
    payload["tenure"] = 999999
    r = client.post("/predict", json=payload)
    assert r.status_code == 400
    assert "details" in r.get_json()


def test_bad_category_returns_400(client):
    payload = load("sample.json")
    payload["Contract"] = "Lifetime"
    r = client.post("/predict", json=payload)
    assert r.status_code == 400


@pytest.mark.parametrize("tenure,expected", [
    (0, "0-1yr"), (12, "0-1yr"), (13, "1-2yr"),
    (24, "1-2yr"), (48, "2-4yr"), (49, "4yr+"),
])
def test_tenure_group_boundaries(tenure, expected):
    assert tenure_group(tenure) == expected