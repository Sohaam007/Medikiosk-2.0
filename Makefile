.PHONY: test backend-test frontend-build lint typecheck hygiene verify

test:
	uv run --extra dev python -m pytest tests/ -q

backend-test:
	uv run --extra dev python -m pytest tests/ -q

frontend-build:
	cd frontend && npm run build

lint:
	uv run --extra dev ruff check src/ tests/

typecheck:
	uv run --extra dev mypy src/ --strict

hygiene:
	python scripts/check_repo_hygiene.py

verify: hygiene test lint typecheck frontend-build
