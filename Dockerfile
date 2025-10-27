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

# Install Google Cloud CLI
RUN curl https://sdk.cloud.google.com | bash
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

# Install Oracle Cloud CLI
RUN curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash -s -- --accept-all-defaults
ENV PATH="/root/bin:${PATH}"

# Install IBM Cloud CLI
RUN curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
ENV PATH="/root/.bluemix/bin:${PATH}"

# Install Node.js and Wrangler CLI for Cloudflare Pages
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g wrangler \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform visualization tools
RUN curl -sSLo terraform-docs https://github.com/terraform-docs/terraform-docs/releases/download/v0.16.0/terraform-docs-v0.16.0-linux-amd64 \
    && chmod +x terraform-docs \
    && mv terraform-docs /usr/local/bin/

# Install Rover (Terraform state visualizer) - alternative approach
RUN curl -sSL https://github.com/im2nguyen/rover/releases/download/v0.3.0/rover_0.3.0_linux_amd64 -o rover \
    && chmod +x rover \
    && mv rover /usr/local/bin/

# Install Graphviz for diagram generation
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

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

# Create a flexible entrypoint that allows cloud CLI and visualization commands
RUN echo '#!/bin/bash\n\
if [ "$1" = "aws" ]; then\n\
    shift\n\
    exec aws "$@"\n\
elif [ "$1" = "gcloud" ]; then\n\
    shift\n\
    exec gcloud "$@"\n\
elif [ "$1" = "oci" ]; then\n\
    shift\n\
    exec oci "$@"\n\
elif [ "$1" = "ibmcloud" ]; then\n\
    shift\n\
    exec ibmcloud "$@"\n\
elif [ "$1" = "terraform" ]; then\n\
    shift\n\
    exec terraform "$@"\n\
elif [ "$1" = "terraform-docs" ]; then\n\
    shift\n\
    exec terraform-docs "$@"\n\
elif [ "$1" = "rover" ]; then\n\
    shift\n\
    exec rover "$@"\n\
elif [ "$1" = "dot" ]; then\n\
    shift\n\
    exec dot "$@"\n\
elif [ "$1" = "wrangler" ]; then\n\
    shift\n\
    exec wrangler "$@"\n\
elif [ "$1" = "bash" ] || [ "$1" = "sh" ]; then\n\
    exec "$@"\n\
else\n\
    exec /usr/local/bin/docker-entrypoint.sh "$@"\n\
fi' > /usr/local/bin/flexible-entrypoint.sh && chmod +x /usr/local/bin/flexible-entrypoint.sh

# Default command
ENTRYPOINT ["/usr/local/bin/flexible-entrypoint.sh"]
CMD ["help"]
