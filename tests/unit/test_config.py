"""Validation of :class:`GameConfig` constraints."""

from __future__ import annotations

import pytest

from highway.domain import GameConfig
from highway.domain.errors import InvalidConfigError


def test_default_config_is_valid():
    cfg = GameConfig()
    assert cfg.lanes >= 2
    assert cfg.player_row < cfg.playfield_height
    assert cfg.collision_top <= cfg.player_row


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lanes": 1},
        {"player_row": 22, "playfield_height": 22},
        {"collision_top": 25},
        {"initial_speed": 0},
        {"max_speed": 0.0},
        {"initial_lives": 0},
        {"speed_threshold": 0},
    ],
)
def test_invalid_configs_raise(kwargs):
    with pytest.raises(InvalidConfigError):
        GameConfig(**kwargs)
