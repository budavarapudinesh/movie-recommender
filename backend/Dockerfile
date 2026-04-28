FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Render injects $PORT; fall back to 8000 for local Docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
