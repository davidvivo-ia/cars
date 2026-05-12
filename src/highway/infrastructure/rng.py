"""Seedable random number generator implementing :class:`Rng`."""

from __future__ import annotations

import random
import time


class SeededRng:
    """Wrap :class:`random.Random` with the :class:`~highway.domain.rng.Rng` API.

    If no ``seed`` is supplied, the constructor draws one from
    ``time.time_ns()`` and exposes it via :attr:`seed` so callers (and
    the scoreboard) can record exactly what produced the run.

    Args:
        seed: Optional integer seed. ``None`` triggers a clock-based seed.
    """

    __slots__ = ("_random", "seed")

    seed: int

    def __init__(self, seed: int | None = None) -> None:
        actual = seed if seed is not None else time.time_ns() & 0xFFFFFFFF
        self.seed = actual
        self._random = random.Random(actual)

    def integer(self, low: int, high: int) -> int:
        """Return a random integer in ``[low, high]``."""
        return self._random.randint(low, high)

    def fraction(self) -> float:
        """Return a random float in ``[0.0, 1.0)``."""
        return self._random.random()
