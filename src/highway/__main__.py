"""Permite `python -m highway`."""

from __future__ import annotations

from highway.presentation.cli import app


def main() -> None:
    """Run the Typer application as a module entrypoint."""
    app()


if __name__ == "__main__":  # pragma: no cover - thin entry
    main()
