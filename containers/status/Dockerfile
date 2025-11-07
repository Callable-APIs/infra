# CallableAPIs Status Container
# Aggregates health and status information from all infrastructure nodes

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY containers/status/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy clint module from repo root
COPY clint/ ./clint/

# Create container version file
COPY containers/status/CONTAINER_VERSION /etc/CONTAINER_VERSION

# Create non-root user
RUN useradd -m -u 1000 statususer && \
    chown -R statususer:statususer /app

# Switch to non-root user
USER statususer

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application using clint
CMD ["python", "-m", "clint", "container", "status"]
