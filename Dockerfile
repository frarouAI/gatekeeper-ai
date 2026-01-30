FROM python:3.11-slim

LABEL maintainer="frankroux@gmail.com"
LABEL description="Gatekeeper AI - Autonomous Code Quality"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY setup.py pyproject.toml README.md ./
COPY gatekeeper_ai/ ./gatekeeper_ai/

# Install package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 gatekeeper && \
    chown -R gatekeeper:gatekeeper /app

USER gatekeeper

# Set entrypoint
ENTRYPOINT ["gatekeeper"]
CMD ["--help"]
