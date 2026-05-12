"""Pure render helpers that turn a ``GameState`` into a Rich :class:`Text`.

Kept separate from the Textual app so that headless tests can render
frames as plain strings (useful for ``--demo --headless`` and snapshot
tests).
"""

from __future__ import annotations

from rich.text import Text

from highway.domain import GameState

# Glyphs and palette ----------------------------------------------
LANE_WIDTH = 4
ROAD_COLOR = "#0e1014"
LANE_LINE = "#3a3f4a"
SHOULDER = "#1a1d24"
PLAYER_COLOR = "#ffcc00"
OBSTACLE_COLOR = "#ff3344"
GRASS = "#1f5e2a"


def render_frame(state: GameState) -> Text:
    """Return a Rich :class:`Text` with the current frame rendered.

    The output uses a fixed grid of size ``config.playfield_height``
    rows by ``config.lanes * LANE_WIDTH`` columns plus shoulders.
    """
    cfg = state.config
    text = Text()

    obstacles_by_pos: dict[tuple[int, int], None] = {
        (obs.visible_row, obs.lane): None
        for obs in state.obstacles
        if 0 <= obs.visible_row < cfg.playfield_height
    }

    for row in range(cfg.playfield_height):
        # left shoulder
        text.append("░░", style=f"{GRASS}")
        text.append("│", style=SHOULDER)
        for lane in range(cfg.lanes):
            for col in range(LANE_WIDTH):
                if (row, lane) in obstacles_by_pos and col == LANE_WIDTH // 2:
                    text.append("█", style=f"bold {OBSTACLE_COLOR}")
                elif row == cfg.player_row and lane == state.player_lane and col == LANE_WIDTH // 2:
                    text.append("▲", style=f"bold {PLAYER_COLOR}")
                elif col == 0 and lane > 0 and row % 2 == state.tick % 2:
                    text.append("┊", style=LANE_LINE)
                else:
                    text.append(" ", style=ROAD_COLOR)
        text.append("│", style=SHOULDER)
        text.append("░░\n", style=GRASS)

    return text


def render_status(state: GameState, best_score: int) -> Text:
    """Return a status line summarising score, lives, speed and best."""
    text = Text()
    text.append(" PT ", style="bold #ffcc00")
    text.append(f"{state.score:>6} ", style="bold #f4f4f5")
    text.append(" VID ", style="bold #ff3344")
    text.append("♥" * state.lives + "·" * (state.config.initial_lives - state.lives))
    text.append(f"  VEL {state.speed:>4.2f}", style="#ff8a3d")
    text.append(f"   REC {best_score:>6}", style="#33ff66")
    return text
