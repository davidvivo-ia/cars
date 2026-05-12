"""Tunable knobs for the Road Racer 2026 simulation."""

from __future__ import annotations

from dataclasses import dataclass

from highway.domain.errors import InvalidConfigError


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Configuration parameters for a single game.

    Attributes:
        lanes: Number of parallel lanes on the road (always >= 2).
        playfield_height: Number of rows from the top of the road to
            the line where the player sits (inclusive).
        player_row: Row in which the player's car stays anchored.
        collision_top: Top row of the collision band (inclusive).
        initial_speed: Initial vertical speed in rows per tick.
        max_speed: Hard cap for speed in rows per tick.
        speed_increment: How much speed grows when the threshold hits.
        speed_threshold: Score interval that triggers a speed bump.
        initial_lives: Lives the player starts with.
        obstacles_per_lane: Obstacles tracked simultaneously per lane.
    """

    lanes: int = 4
    playfield_height: int = 22
    player_row: int = 20
    collision_top: int = 18
    initial_speed: float = 0.5
    max_speed: float = 2.5
    speed_increment: float = 0.1
    speed_threshold: int = 200
    initial_lives: int = 3
    obstacles_per_lane: int = 1

    def __post_init__(self) -> None:
        if self.lanes < 2:
            raise InvalidConfigError("Se requieren al menos 2 carriles")
        if self.player_row >= self.playfield_height:
            raise InvalidConfigError("player_row debe ser < playfield_height")
        if self.collision_top > self.player_row:
            raise InvalidConfigError("collision_top debe ser <= player_row")
        if self.initial_speed <= 0:
            raise InvalidConfigError("initial_speed debe ser positivo")
        if self.max_speed < self.initial_speed:
            raise InvalidConfigError("max_speed debe ser >= initial_speed")
        if self.initial_lives <= 0:
            raise InvalidConfigError("initial_lives debe ser positivo")
        if self.speed_threshold <= 0:
            raise InvalidConfigError("speed_threshold debe ser positivo")
