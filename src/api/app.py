from flask import Flask, jsonify, request
from flask_cors import CORS

from src.api.config import REQUIRED_FIELDS
from src.api.model_service import ChurnService

app = Flask(__name__)
CORS(app)
service = ChurnService()


def validate(payload):
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400
    return None


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True)
    error = validate(payload)
    if error:
        return error
    try:
        return jsonify(service.predict(payload)), 200
    except Exception as exc:
        return jsonify({"error": f"Could not process input: {exc}"}), 400


@app.route("/explain", methods=["POST"])
def explain():
    payload = request.get_json(silent=True)
    error = validate(payload)
    if error:
        return error
    try:
        return jsonify(service.explain(payload)), 200
    except Exception as exc:
        return jsonify({"error": f"Could not process input: {exc}"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)