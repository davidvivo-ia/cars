"""Domain-level exceptions for Road Racer 2026."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all errors raised by the pure domain layer."""


class InvalidLaneError(DomainError):
    """Raised when a lane index is outside the configured range."""

    def __init__(self, lane: int, lanes: int) -> None:
        super().__init__(f"Carril {lane} fuera de rango [0, {lanes - 1}]")
        self.lane = lane
        self.lanes = lanes


class InvalidConfigError(DomainError):
    """Raised when game configuration parameters are inconsistent."""
