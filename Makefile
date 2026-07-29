.PHONY: install install-dev run dry-run test lint format typecheck clean help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install package (editable)
	pip install -e .

install-dev: ## Install package with dev dependencies
	pip install -e ".[dev]"

run: ## Run the content crew (TOPIC="..." optional)
	content-crew run --topic "$(or $(TOPIC),Latest Generative AI breakthroughs)"

dry-run: ## Run without calling live LLMs / tools
	CONTENT_CREW_DRY_RUN=true content-crew run --topic "$(or $(TOPIC),Latest Generative AI breakthroughs)" --dry-run

test: ## Run unit tests
	pytest

lint: ## Lint with ruff
	ruff check src tests

format: ## Format with ruff
	ruff format src tests

typecheck: ## Static type check
	mypy src

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
