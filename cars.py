"""Lanzador rápido para Road Racer 2026.

Equivale a ``uv run highway`` pero sin depender de ``uv``: basta con
ejecutar ``python cars.py`` desde la raíz del repo siempre que las
dependencias estén instaladas (``pip install -e .`` o ``uv sync``).

Soporta los mismos flags que el CLI:

    python cars.py
    python cars.py --demo
    python cars.py --demo --seed 42 --headless --max-ticks 200
    python cars.py scores
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap() -> None:
    """Asegura que el paquete ``highway`` esté en ``sys.path``.

    Permite ejecutar el script directamente desde una clonación fresca
    sin necesidad de ``pip install -e .`` (Textual, Typer, etc. sí
    deben estar instalados, pero no es obligatorio instalar el
    paquete en sí).
    """
    src = Path(__file__).resolve().parent / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _missing_dependency_message(exc: ModuleNotFoundError) -> str:
    return (
        f"Falta la dependencia '{exc.name}'.\n\n"
        "Instala el juego con una de estas opciones:\n"
        "  1) uv sync --all-extras       (recomendado)\n"
        "  2) pip install -e .\n"
        "  3) pip install textual typer pydantic structlog platformdirs rich\n"
    )


def main() -> None:
    _bootstrap()
    try:
        from highway.presentation.cli import app  # noqa: PLC0415
    except ModuleNotFoundError as exc:
        sys.stderr.write(_missing_dependency_message(exc))
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
