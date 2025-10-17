# Multi-stage build for AWS Infrastructure Reporting Tool with Terraform
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    jq \
    ansible \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
ARG TERRAFORM_VERSION=1.6.6
RUN curl -fsSL https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy application code first
COPY src/ ./src/
COPY config.yaml.example ./
COPY README.md ./

# Install Python dependencies
RUN poetry install --only=main --no-root

# Create directories for reports
RUN mkdir -p reports internal_reports terraform_output

# Set environment variables
ENV PYTHONPATH=/app
ENV AWS_DEFAULT_REGION=us-east-1

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create a flexible entrypoint that allows AWS CLI commands
RUN echo '#!/bin/bash\n\
if [ "$1" = "aws" ]; then\n\
    shift\n\
    exec aws "$@"\n\
elif [ "$1" = "terraform" ]; then\n\
    shift\n\
    exec terraform "$@"\n\
elif [ "$1" = "bash" ] || [ "$1" = "sh" ]; then\n\
    exec "$@"\n\
else\n\
    exec /usr/local/bin/docker-entrypoint.sh "$@"\n\
fi' > /usr/local/bin/flexible-entrypoint.sh && chmod +x /usr/local/bin/flexible-entrypoint.sh

# Default command
ENTRYPOINT ["/usr/local/bin/flexible-entrypoint.sh"]
CMD ["help"]
