"""Shared fixtures and helpers for the test suite."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from highway.domain import GameConfig
from highway.infrastructure import SeededRng


@dataclass(slots=True)
class FixedRng:
    """Deterministic Rng yielding a single fixed integer and zero floats."""

    fixed_int: int = 0

    def integer(self, low: int, high: int) -> int:
        return max(low, min(high, self.fixed_int))

    def fraction(self) -> float:  # pragma: no cover - trivial
        return 0.0


@pytest.fixture
def config() -> GameConfig:
    return GameConfig()


@pytest.fixture
def rng() -> SeededRng:
    return SeededRng(seed=42)


@pytest.fixture
def fixed_rng() -> FixedRng:
    return FixedRng()
