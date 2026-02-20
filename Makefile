.PHONY: dev run stop lint format test clean

dev:
	uv run uvicorn app.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

run:
	uv run uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8000

stop:
	pkill -f uvicorn 2>/dev/null; pkill -f "python.*main" 2>/dev/null; pkill -f "app.main" 2>/dev/null; echo "✅ Server stopped"

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

test:
	uv run pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; \
	rm -rf .venv
