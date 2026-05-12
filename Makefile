.PHONY: install play demo headless test lint format type check scores clean

# Resuelve un intérprete adecuado:
#   1) el del venv local (`.venv/bin/python`) si existe;
#   2) `uv run python` si uv está disponible;
#   3) `python3` del sistema.
PY := $(shell \
	if [ -x .venv/bin/python ]; then \
		echo .venv/bin/python; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "uv run python"; \
	else \
		echo python3; \
	fi)

install:
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --all-extras; \
	else \
		$(PY) -m pip install -e ".[dev]"; \
	fi

play:
	$(PY) cars.py

demo:
	$(PY) cars.py --demo

headless:
	$(PY) cars.py --demo --seed 42 --headless --max-ticks 200

scores:
	$(PY) cars.py scores

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check .

format:
	$(PY) -m ruff format .

type:
	$(PY) -m mypy --strict src

check: format lint type test

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
