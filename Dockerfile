# Multi-stage Dockerfile for Retail Operations Dashboard
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/logs /app/models

# Expose ports
EXPOSE 5000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Default command (can override)
CMD ["python", "app.py"]

# Development stage
FROM base as development

# Install dev dependencies
RUN pip install --no-cache-dir jupyter jupyterlab ipython pytest pytest-cov

# Copy all files
COPY . .

EXPOSE 8888 5000

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
