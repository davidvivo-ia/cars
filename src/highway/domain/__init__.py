"""Pure domain layer for Road Racer 2026."""

from highway.domain.config import GameConfig
from highway.domain.errors import DomainError, InvalidLaneError
from highway.domain.intents import Intent
from highway.domain.rng import Rng
from highway.domain.scoreboard import ScoreboardRepository, ScoreEntry
from highway.domain.state import GameState, Obstacle, Phase
from highway.domain.step import initial_state, step

__all__ = [
    "DomainError",
    "GameConfig",
    "GameState",
    "Intent",
    "InvalidLaneError",
    "Obstacle",
    "Phase",
    "Rng",
    "ScoreEntry",
    "ScoreboardRepository",
    "initial_state",
    "step",
]
