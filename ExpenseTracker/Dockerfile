# ───────────────────────────────────────────────────────────────────────────────
# Expense Tracker — Dockerfile
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="DevOps Student" \
      project="Expense Tracker CI/CD" \
      version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies (keep image slim)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create the persistent data directory
# (will be overridden by a Docker Volume mount at runtime)
RUN mkdir -p /app/data

# Expose Flask port
EXPOSE 5000

# Health check — polls the dashboard every 30 seconds
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start the application
CMD ["python", "app.py"]
