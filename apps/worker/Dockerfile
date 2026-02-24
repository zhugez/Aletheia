FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY apps/worker/requirements.txt ./requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    MINERU_DEVICE_MODE=cpu \
    MINERU_VIRTUAL_VRAM_SIZE=0

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 curl && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -m appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --find-links=/wheels /wheels/* && rm -rf /wheels

COPY . /app
WORKDIR /app/apps/worker
USER appuser

CMD ["python", "worker.py"]
