.PHONY: test backend-test frontend-build lint typecheck

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
