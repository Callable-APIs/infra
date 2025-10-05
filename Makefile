.PHONY: help install install-dev test lint format type-check security clean run demo

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install all dependencies including dev
	poetry install
	poetry run pre-commit install

test: ## Run tests
	poetry run pytest

test-cov: ## Run tests with coverage
	poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting
	poetry run pylint src/

format: ## Format code
	poetry run black src/ tests/
	poetry run isort src/ tests/

type-check: ## Run type checking
	poetry run mypy src/

security: ## Run security checks
	poetry run bandit -r src/

check-all: lint type-check security test ## Run all checks

clean: ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf demo_reports/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run: ## Run the application (public report)
	poetry run aws-infra-report

run-internal: ## Run internal detailed HTML report
	poetry run aws-infra-report --internal

run-console: ## Run internal report to console only
	poetry run aws-infra-report --internal --console-only

view-internal: ## Open internal HTML report in browser
	open reports/index.html

demo: ## Run demo with mock data
	poetry run python example.py

setup-github-pages: ## Setup GitHub Pages deployment
	./setup-github-pages.sh

test-github-pages: ## Test GitHub Pages report generation
	poetry run aws-infra-report --days 7 --output test_reports

# Docker commands
docker-build: ## Build Docker image
	./run-docker.sh build

docker-cost-report: ## Generate cost report in Docker container
	./run-docker.sh cost-report

docker-internal-report: ## Generate internal cost report in Docker container
	./run-docker.sh cost-report --internal

docker-discover: ## Discover AWS infrastructure in Docker container
	./run-docker.sh terraform-discover

docker-generate: ## Generate Terraform configuration in Docker container
	./run-docker.sh terraform-generate

docker-plan: ## Run terraform plan in Docker container
	./run-docker.sh terraform-plan

docker-full-analysis: ## Run complete analysis in Docker container
	./run-docker.sh full-analysis

docker-shell: ## Open shell in Docker container
	./run-docker.sh shell

docker-clean: ## Clean up Docker containers and images
	./run-docker.sh clean

build: ## Build the package
	poetry build

publish: ## Publish to PyPI (requires authentication)
	poetry publish

update: ## Update dependencies
	poetry update
