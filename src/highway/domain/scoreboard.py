"""Scoreboard value object and repository protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    """One record in the high scores table.

    Attributes:
        name: Player or bot name. ``"DEMO"`` denotes a demo run.
        score: Final score reached during the game.
        speed: Final speed at game over.
        seed: RNG seed used in the run (0 if unseeded).
        ticks: Tick count at game over (for tie breaking).
    """

    name: str
    score: int
    speed: float
    seed: int
    ticks: int


class ScoreboardRepository(Protocol):
    """Protocol for persisting and querying high scores."""

    def load(self) -> tuple[ScoreEntry, ...]:
        """Return all stored entries, best score first."""

    def add(self, entry: ScoreEntry) -> tuple[ScoreEntry, ...]:
        """Insert *entry* and return the updated top list."""
