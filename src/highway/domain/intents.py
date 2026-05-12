"""Player intents for a single game tick."""

from __future__ import annotations

from enum import Enum


class Intent(Enum):
    """High-level command the player issues this tick.

    Mirrors the original Sinclair BASIC controls: O moves left, P moves
    right, anything else keeps the lane.
    """

    NONE = "none"
    LEFT = "left"
    RIGHT = "right"
    PAUSE = "pause"
    QUIT = "quit"
