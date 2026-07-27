FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/src
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
COPY backend/requirements.txt /app/backend-requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt \
    && python -m pip install -r /app/backend-requirements.txt
COPY . .
EXPOSE 8000
