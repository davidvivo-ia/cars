"""Smoke tests for the render helpers."""

from __future__ import annotations

from highway.domain import initial_state
from highway.presentation.render import render_frame, render_status


def test_render_frame_has_one_line_per_row(config, rng):
    state = initial_state(config, rng)
    text = render_frame(state)
    lines = text.plain.splitlines()
    assert len(lines) == config.playfield_height


def test_render_status_mentions_score_and_lives(config, rng):
    state = initial_state(config, rng)
    text = render_status(state, best_score=999)
    plain = text.plain
    assert "999" in plain
    assert "♥" in plain
    assert "VEL" in plain
