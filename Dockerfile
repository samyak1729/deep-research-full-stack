# Multi-stage build for Deep Research fullstack app

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY app/ ./app/

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --frozen

# Stage 2: Runtime Backend
FROM python:3.11-slim as backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --from=builder /app/src ./src
COPY --from=builder /app/app ./app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app/backend/main.py"]

# Stage 3: Runtime Frontend
FROM python:3.11-slim as frontend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --from=builder /app/src ./src
COPY --from=builder /app/app ./app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
