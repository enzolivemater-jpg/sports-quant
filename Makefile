.PHONY: sync format lint typecheck test test-unit test-integration check db-up db-down db-test-up db-test-down migrate migration-status validate-f1

sync:
	uv sync --all-groups

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

test:
	uv run pytest

test-unit:
	uv run pytest -m "not integration"

test-integration:
	uv run pytest -m integration

validate-f1:
	uv run python scripts/validate_f1.py

check: validate-f1 lint typecheck test-unit

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-test-up:
	docker compose --profile test up -d postgres-test

db-test-down:
	docker compose --profile test stop postgres-test

migrate:
	uv run alembic upgrade head

migration-status:
	uv run alembic heads
