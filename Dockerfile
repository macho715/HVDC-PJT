# HVDC Logistics System Dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MACHO_MODE=PRODUCTION

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/output /app/logs /app/tests

# Set permissions
RUN chmod +x /app/start_all_mcp_servers.ps1 /app/start_all_mcp_servers.bat

# Create non-root user
RUN useradd --create-home --shell /bin/bash hvdc && \
    chown -R hvdc:hvdc /app
USER hvdc

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "src/main.py"]
