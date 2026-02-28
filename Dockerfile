# ─── Stage 1: Builder ────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.11-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies into the venv (without app code for better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy app source and install the project itself
COPY . .
RUN uv sync --frozen --no-dev


# ─── Stage 2: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy only the venv from builder — no uv, no build tools in final image
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY --chown=appuser:appgroup . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
