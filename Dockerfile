FROM python:3.11-slim

# Install sshpass
RUN apt-get update && \
    apt-get install -y sshpass openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY cellwan_exporter.py .

# Create non-root user
RUN useradd -m -u 1000 exporter && \
    chown -R exporter:exporter /app

USER exporter

# Expose default port
EXPOSE 9101

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9101/').read()" || exit 1

ENTRYPOINT ["python", "cellwan_exporter.py"]
