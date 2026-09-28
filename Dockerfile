FROM python:3.12-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/ ./src/
COPY models/ ./models/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.api.app:app"]