"""Behavioural tests for :class:`DemoBot`."""

from __future__ import annotations

from dataclasses import replace

from highway.application import DemoBot
from highway.domain import Intent, Obstacle, initial_state


def test_bot_keeps_lane_when_road_is_clear(config, rng):
    state = initial_state(config, rng)
    bot = DemoBot()
    assert bot.decide(state) is Intent.NONE


def test_bot_dodges_left_when_threat_in_lane_and_left_is_clear(config, rng):
    state = initial_state(config, rng)
    state = replace(state, player_lane=2)
    obstacles = (
        Obstacle(lane=2, row=float(config.collision_top)),
        *state.obstacles[1:],
    )
    state = replace(state, obstacles=obstacles)
    bot = DemoBot()
    assert bot.decide(state) is Intent.LEFT


def test_bot_dodges_right_when_left_is_blocked(config, rng):
    state = initial_state(config, rng)
    state = replace(state, player_lane=2)
    blocked_left = (
        Obstacle(lane=2, row=float(config.collision_top)),
        Obstacle(lane=1, row=float(config.collision_top)),
        *state.obstacles[2:],
    )
    state = replace(state, obstacles=blocked_left)
    bot = DemoBot()
    assert bot.decide(state) is Intent.RIGHT


def test_bot_stays_put_when_left_edge_and_blocked(config, rng):
    state = initial_state(config, rng)
    state = replace(state, player_lane=0)
    obstacles = (
        Obstacle(lane=0, row=float(config.collision_top)),
        Obstacle(lane=1, row=float(config.collision_top)),
        *state.obstacles[2:],
    )
    state = replace(state, obstacles=obstacles)
    bot = DemoBot()
    # the bot must always return a valid Intent even when all options are bad
    assert bot.decide(state) in {Intent.LEFT, Intent.RIGHT, Intent.NONE}
