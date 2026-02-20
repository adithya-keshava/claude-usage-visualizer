.PHONY: help setup install dev run stop lint format test clean docs agent-status

help:
	@echo "Claude Usage Visualizer - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          Install dependencies and prepare environment"
	@echo "  make install        Install Python dependencies via uv"
	@echo ""
	@echo "Development:"
	@echo "  make dev            Run development server with auto-reload"
	@echo "  make run            Run production server"
	@echo "  make stop           Stop any running servers"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linter (ruff check)"
	@echo "  make format         Format code with ruff"
	@echo "  make test           Run tests with pytest"
	@echo ""
	@echo "Documentation & Agent Readiness:"
	@echo "  make docs           Show documentation references"
	@echo "  make agent-status   Check agent-readiness status"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove cache, .venv, and build artifacts"
	@echo ""

setup: install
	@echo "✅ Setup complete! Run 'make dev' to start development server"

install:
	uv sync --python 3.11

dev:
	uv run --python 3.11 uvicorn app.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

run:
	uv run --python 3.11 uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8000

stop:
	pkill -f uvicorn 2>/dev/null; pkill -f "python.*main" 2>/dev/null; pkill -f "app.main" 2>/dev/null; echo "✅ Server stopped"

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

test:
	uv run pytest

docs:
	@echo "📚 Documentation References:"
	@echo ""
	@echo "Agent-Readiness:"
	@echo "  - AGENTS.md                          Skills index and quick start"
	@echo "  - .agents/skills/repo-skill/README.md Developer guide with task instructions"
	@echo ""
	@echo "Domain Knowledge (20 modules):"
	@echo "  - Architecture: .agents/skills/repo-skill/modules/domain/architecture/"
	@echo "  - Data Layer:   .agents/skills/repo-skill/modules/domain/data/"
	@echo "  - Frontend:     .agents/skills/repo-skill/modules/domain/frontend/"
	@echo "  - Integration:  .agents/skills/repo-skill/modules/integration/"
	@echo "  - Patterns:     .agents/skills/repo-skill/modules/patterns/"
	@echo ""
	@echo "Progress:"
	@echo "  - BUILD_CHECKLIST.md  Extraction status (73.2% complete)"
	@echo ""

agent-status:
	@if [ -f AGENTS.md ]; then \
		echo "✅ Agent-Ready Repository"; \
		echo ""; \
		echo "Status: $(shell grep 'Status:' AGENTS.md | head -1)"; \
		echo "Documentation: $(shell find .agents/skills/repo-skill/modules -name '*.md' | wc -l) modules"; \
		echo "Progress: $(shell grep 'Overall Progress' BUILD_CHECKLIST.md | grep -oE '[0-9]+/[0-9]+')"; \
		echo ""; \
		echo "Get started: cat AGENTS.md"; \
	else \
		echo "⚠️  Repository is not agent-ready yet"; \
	fi

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; \
	rm -rf .venv
	@echo "✅ Cleanup complete"
