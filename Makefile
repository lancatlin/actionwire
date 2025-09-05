# Python project Makefile
.PHONY: help install run test lint format clean build publish

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using Poetry
	poetry install

install-dev: ## Install development dependencies
	poetry install --with dev

run: ## Run the main application
	poetry run python -m actionwire

test: ## Run tests
	poetry run pytest tests/ -v

test-coverage: ## Run tests with coverage report
	poetry run pytest tests/ --cov=actionwire --cov-report=html --cov-report=term

lint: ## Run linting checks
	poetry run ruff check actionwire/ tests/
	poetry run mypy actionwire/

format: ## Format code using black and isort
	poetry run black actionwire/ tests/
	poetry run isort actionwire/ tests/

format-check: ## Check if code is properly formatted
	poetry run black --check actionwire/ tests/
	poetry run isort --check-only actionwire/ tests/

clean: ## Clean up build artifacts and cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

build: ## Build the package
	poetry build

publish: ## Publish to PyPI (requires authentication)
	poetry publish

publish-test: ## Publish to Test PyPI
	poetry publish --repository testpypi

check: format-check lint test ## Run all checks (format, lint, test)

ci: install check ## Run CI pipeline locally

dev: install-dev ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"
	@echo "Run 'make format' to format code"
