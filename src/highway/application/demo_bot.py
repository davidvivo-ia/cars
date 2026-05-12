"""Deterministic demo bot used by ``--demo`` and end-to-end tests."""

from __future__ import annotations

from highway.domain import GameState, Intent


class DemoBot:
    """Decision policy that plays Road Racer deterministically.

    The bot looks at every obstacle below ``trigger_row`` and shifts
    away from the closest threatening lane. When the player lane is
    clear it stays put; with multiple threats it picks the side with
    the larger gap.
    """

    __slots__ = ("trigger_row",)

    def __init__(self, trigger_row: int | None = None) -> None:
        self.trigger_row = trigger_row

    def decide(self, state: GameState) -> Intent:
        """Return the intent the bot wishes to issue this tick."""
        config = state.config
        trigger = self.trigger_row if self.trigger_row is not None else config.collision_top - 4
        lane = state.player_lane

        threat_in_lane = self._closest_threat_in_lane(state, lane, trigger)
        if threat_in_lane is None:
            return Intent.NONE

        left_gap = self._gap_in_lane(state, lane - 1, trigger) if lane > 0 else float("-inf")
        right_gap = (
            self._gap_in_lane(state, lane + 1, trigger)
            if lane < config.lanes - 1
            else float("-inf")
        )
        if left_gap >= right_gap and left_gap != float("-inf"):
            return Intent.LEFT
        if right_gap != float("-inf"):
            return Intent.RIGHT
        return Intent.NONE

    # ------------------------------------------------- helpers
    @staticmethod
    def _closest_threat_in_lane(state: GameState, lane: int, trigger: int) -> float | None:
        """Return ``row`` of the closest obstacle in *lane* below *trigger*, or ``None``."""
        rows = [obs.row for obs in state.obstacles if obs.lane == lane and obs.row >= trigger]
        return min(rows) if rows else None

    @staticmethod
    def _gap_in_lane(state: GameState, lane: int, trigger: int) -> float:
        """Return the distance to the closest obstacle in *lane* below *trigger*."""
        rows = [obs.row for obs in state.obstacles if obs.lane == lane and obs.row >= trigger]
        if not rows:
            return float("inf")
        return min(rows) - trigger
