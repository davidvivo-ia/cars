"""GameLoop: thin orchestrator around the pure ``step`` reducer."""

from __future__ import annotations

from dataclasses import dataclass

from highway.domain import (
    GameConfig,
    GameState,
    Intent,
    Phase,
    Rng,
    ScoreboardRepository,
    ScoreEntry,
    initial_state,
    step,
)


@dataclass(frozen=True, slots=True)
class RunSummary:
    """Result of a finished run."""

    final_state: GameState
    ticks_played: int
    new_top_list: tuple[ScoreEntry, ...]


class GameLoop:
    """Orchestrate one game from start to finish.

    The loop owns the current :class:`GameState`, applies player
    intents, and forwards everything to the pure domain ``step``.
    """

    __slots__ = ("_config", "_rng", "_scoreboard", "_state")

    def __init__(
        self,
        config: GameConfig,
        rng: Rng,
        scoreboard: ScoreboardRepository,
    ) -> None:
        self._config = config
        self._rng = rng
        self._scoreboard = scoreboard
        self._state = initial_state(config, rng)

    # -------------------------------------------------- properties
    @property
    def state(self) -> GameState:
        """Read-only view of the current game state."""
        return self._state

    @property
    def is_over(self) -> bool:
        """True when the game has reached ``Phase.GAME_OVER``."""
        return self._state.phase is Phase.GAME_OVER

    # -------------------------------------------------- methods
    def step(self, intent: Intent) -> GameState:
        """Apply *intent* and advance one tick."""
        self._state = step(self._state, intent, self._rng)
        return self._state

    def reset(self) -> GameState:
        """Begin a fresh game with the same configuration and RNG."""
        self._state = initial_state(self._config, self._rng)
        return self._state

    def finalize(self, player_name: str, seed: int) -> RunSummary:
        """Persist the result and return a :class:`RunSummary`."""
        entry = ScoreEntry(
            name=player_name[:12] or "PLAYER",
            score=self._state.score,
            speed=round(self._state.speed, 2),
            seed=seed,
            ticks=self._state.tick,
        )
        top = self._scoreboard.add(entry)
        return RunSummary(
            final_state=self._state,
            ticks_played=self._state.tick,
            new_top_list=top,
        )
