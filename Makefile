.PHONY: help install install-dev clean test lint format run

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	uv pip install -e .

install-dev:  ## Install the package with dev dependencies
	uv pip install -e ".[dev,jupyter]"

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:  ## Run tests
	pytest

lint:  ## Run linting checks
	ruff check .

format:  ## Format code
	ruff format .

docs:  ## Generate API documentation
	pdoc schema_sentinel -o docs

setup-env:  ## Set up virtual environment with uv
	uv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate  # Linux/macOS"
	@echo "  .venv\\Scripts\\activate    # Windows"

init: setup-env  ## Initialize project (create venv and install)
	@echo "Installing dependencies..."
	uv pip install -e ".[dev,jupyter]"
	@echo ""
	@echo "Setup complete! Activate the virtual environment with:"
	@echo "  source .venv/bin/activate  # Linux/macOS"
