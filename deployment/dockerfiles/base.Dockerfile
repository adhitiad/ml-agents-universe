# Multi-stage Base Image untuk ML Agents Universe
# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Setup build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (asumsikan requirements.txt dibuat sebelum build)
# Di environment lokal ini kita akan install langsung package standar
RUN pip install --user --no-cache-dir \
    fastapi uvicorn httpx pydantic langgraph langchain-core pytest

# ---
# Runtime stage
FROM python:3.11-slim

# Buat non-root user
RUN useradd -m -s /bin/bash universe_user

# Set working directory
WORKDIR /app

# Copy installed packages dari builder
COPY --from=builder /root/.local /home/universe_user/.local

# Pastikan local bin masuk PATH
ENV PATH=/home/universe_user/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy seluruh source code
COPY --chown=universe_user:universe_user . /app

# Gunakan non-root user
USER universe_user
