"""Random number generator protocol used by the domain.

The domain never touches Python's global :mod:`random`. Any randomness
enters through an :class:`Rng` injected by the application layer, which
makes the entire simulation deterministic when seeded.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Rng(Protocol):
    """Minimum random number surface required by the domain."""

    def integer(self, low: int, high: int) -> int:
        """Return a random integer in ``[low, high]``, both inclusive."""

    def fraction(self) -> float:
        """Return a random float in ``[0.0, 1.0)``."""
