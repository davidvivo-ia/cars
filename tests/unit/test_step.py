"""Unit tests for the pure :func:`step` reducer."""

from __future__ import annotations

from dataclasses import replace

import pytest

from highway.domain import GameConfig, Intent, Obstacle, Phase, initial_state, step
from highway.domain.errors import InvalidLaneError


def test_initial_state_has_full_lives_and_playing_phase(config, rng):
    state = initial_state(config, rng)
    assert state.lives == config.initial_lives
    assert state.phase is Phase.PLAYING
    assert state.score == 0
    assert len(state.obstacles) == config.lanes
    assert all(obstacle.row < 0 for obstacle in state.obstacles)


def test_intent_left_decreases_lane(config, rng):
    state = initial_state(config, rng)
    next_state = step(state, Intent.LEFT, rng)
    assert next_state.player_lane == max(0, state.player_lane - 1)


def test_intent_right_increases_lane(config, rng):
    state = initial_state(config, rng)
    next_state = step(state, Intent.RIGHT, rng)
    assert next_state.player_lane == min(config.lanes - 1, state.player_lane + 1)


def test_intent_at_boundary_stays_clamped(config, rng):
    state = initial_state(config, rng)
    leftmost = replace(state, player_lane=0)
    rightmost = replace(state, player_lane=config.lanes - 1)
    assert step(leftmost, Intent.LEFT, rng).player_lane == 0
    assert step(rightmost, Intent.RIGHT, rng).player_lane == config.lanes - 1


def test_tick_counter_advances(config, rng):
    state = initial_state(config, rng)
    next_state = step(state, Intent.NONE, rng)
    assert next_state.tick == state.tick + 1


def test_obstacles_move_down_by_speed(config, rng):
    state = initial_state(config, rng)
    # snap obstacles to known rows so the assertion is deterministic
    obstacles = tuple(replace(obs, row=float(idx)) for idx, obs in enumerate(state.obstacles))
    state = replace(state, obstacles=obstacles)
    next_state = step(state, Intent.NONE, rng)
    expected = [round(state.obstacles[i].row + state.speed, 6) for i in range(config.lanes)]
    actual = [round(o.row, 6) for o in next_state.obstacles]
    assert actual == expected


def test_collision_reduces_lives(config, rng):
    state = initial_state(config, rng)
    # plant an obstacle right on the player
    obstacles = (
        Obstacle(lane=state.player_lane, row=float(config.player_row)),
        *state.obstacles[1:],
    )
    crashed = step(replace(state, obstacles=obstacles), Intent.NONE, rng)
    assert crashed.lives == state.lives - 1
    assert crashed.crash_flash > 0


def test_zero_lives_transitions_to_game_over(config, fixed_rng):
    state = initial_state(config, fixed_rng)
    # plant an obstacle right on the player and force lives to 1
    obstacles = (
        Obstacle(lane=state.player_lane, row=float(config.player_row)),
        *state.obstacles[1:],
    )
    one_life = replace(state, obstacles=obstacles, lives=1)
    after = step(one_life, Intent.NONE, fixed_rng)
    assert after.lives == 0
    assert after.phase is Phase.GAME_OVER


def test_game_over_is_absorbing(config, rng):
    state = initial_state(config, rng)
    over = replace(state, phase=Phase.GAME_OVER)
    assert step(over, Intent.RIGHT, rng) is over


def test_score_grows_each_tick(config, rng):
    state = initial_state(config, rng)
    after = step(state, Intent.NONE, rng)
    assert after.score > state.score


def test_speed_caps_at_max(config, rng):
    state = initial_state(config, rng)
    near_max = replace(state, speed=config.max_speed, score=config.speed_threshold - 1)
    after = step(near_max, Intent.NONE, rng)
    assert after.speed <= config.max_speed


def test_step_does_not_mutate_input(config, rng):
    state = initial_state(config, rng)
    snapshot = (state.player_lane, state.score, state.lives, state.tick)
    _ = step(state, Intent.LEFT, rng)
    assert (state.player_lane, state.score, state.lives, state.tick) == snapshot


def test_invalid_lane_error_carries_context():
    cfg = GameConfig(lanes=4)
    with pytest.raises(InvalidLaneError) as exc_info:
        raise InvalidLaneError(99, cfg.lanes)
    assert exc_info.value.lane == 99
    assert exc_info.value.lanes == cfg.lanes
