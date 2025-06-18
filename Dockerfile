# Dockerfile for InfluencerFlow AI Platform
# Lightweight & Fast Build - Core Features Only
# Reference: https://docs.astral.sh/uv/guides/integration/docker/

FROM python:3.11-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV UV_SYSTEM_PYTHON=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock ./

# Install ONLY core dependencies (no ML) for fast build
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the entire project
COPY . .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Set default environment variables for Hugging Face
ENV HOST=0.0.0.0
ENV PORT=7860
ENV DEMO_MODE=true
ENV MOCK_CALLS=true
ENV DEBUG=false

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose the port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Command to run the application  
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 