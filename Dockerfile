# ── Stage 1: dependency layer (cached by Docker unless requirements.txt changes) ──
FROM python:3.11-slim AS deps

WORKDIR /app

# Install system libs needed by soundfile / pydub / numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first — Docker caches this layer.
# The pip install layer is ONLY rebuilt when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: app layer (rebuilt on every code push — fast, just copying files) ──
FROM deps AS app

WORKDIR /app

# Copy source code and data
COPY src/ ./src/
COPY data/ ./data/

# Create logs dir so gunicorn doesn't fail on first start
RUN mkdir -p logs/audio logs/metrics

ENV PYTHONUNBUFFERED=1
ENV SKIP_VECTOR_INDEX=1

EXPOSE 8000

CMD ["gunicorn", "-w", "1", "--threads", "6", "-b", "0.0.0.0:8000", "--timeout", "120", "--chdir", "src", "web_call_app:app"]
