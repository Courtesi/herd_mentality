# Build stage - Install dependencies with uv
FROM python:3.11-slim AS builder

# Copy uv from official image (pinned version for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Environment variables for uv optimization
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (cached separately from app code)
# --no-install-project: Install deps but not the project itself yet
# --no-dev: Skip development dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy application code
COPY api/ ./api/
COPY exchanges/ ./exchanges/
# Keys will be mounted as volume at runtime for better security

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Runtime stage - Minimal production image
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code
COPY --from=builder --chown=appuser:appgroup /app/api /app/api
COPY --from=builder --chown=appuser:appgroup /app/exchanges /app/exchanges
# Keys will be mounted as volume at runtime (not copied into image)

# Set Python path to include virtual environment and app modules
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/api:/app

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check using existing health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/python/health').read()"

# Run the application in production mode (no reload)
# Virtual environment is in PATH, so uvicorn is available directly
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
