"""Immutable game state for Road Racer 2026."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from highway.domain.config import GameConfig


class Phase(Enum):
    """Lifecycle phases for a game."""

    PLAYING = "playing"
    GAME_OVER = "game_over"


@dataclass(frozen=True, slots=True)
class Obstacle:
    """A single rolling obstacle on the road.

    Attributes:
        lane: Lane index where the obstacle currently sits.
        row: Vertical position in rows. May be negative (above screen)
            or fractional between integer rows; the renderer rounds.
    """

    lane: int
    row: float

    @property
    def visible_row(self) -> int:
        """Integer row where the obstacle would be drawn."""
        return int(self.row)


@dataclass(frozen=True, slots=True)
class GameState:
    """Whole game state at one instant in time.

    Attributes:
        config: Tuning constants for this run.
        player_lane: Current lane occupied by the player car.
        obstacles: Active obstacles. Length equals ``config.lanes``.
        score: Accumulated score (monotonically non-decreasing).
        lives: Remaining lives (0 means game over).
        speed: Current vertical speed in rows per tick.
        tick: Tick counter since the game started.
        phase: Lifecycle phase.
        crash_flash: Frames remaining to draw the post-crash flash.
    """

    config: GameConfig
    player_lane: int
    obstacles: tuple[Obstacle, ...]
    score: int
    lives: int
    speed: float
    tick: int
    phase: Phase
    crash_flash: int = 0
