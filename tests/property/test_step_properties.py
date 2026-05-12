"""Property-based tests for the pure reducer."""

from __future__ import annotations

from dataclasses import replace

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from highway.domain import GameConfig, Intent, Phase, initial_state, step
from highway.infrastructure import SeededRng

INTENT_STRATEGY = st.sampled_from([Intent.LEFT, Intent.RIGHT, Intent.NONE])


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    intents=st.lists(INTENT_STRATEGY, min_size=1, max_size=40),
)
def test_lane_stays_in_range(seed, intents):
    config = GameConfig()
    rng = SeededRng(seed)
    state = initial_state(config, rng)
    for intent in intents:
        state = step(state, intent, rng)
        assert 0 <= state.player_lane < config.lanes


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    intents=st.lists(INTENT_STRATEGY, min_size=1, max_size=80),
)
def test_score_is_monotonic_while_playing(seed, intents):
    config = GameConfig()
    rng = SeededRng(seed)
    state = initial_state(config, rng)
    last_score = state.score
    for intent in intents:
        new_state = step(state, intent, rng)
        if state.phase is Phase.PLAYING:
            assert new_state.score >= last_score
            last_score = new_state.score
        state = new_state


@settings(max_examples=100)
@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
def test_speed_never_exceeds_max(seed):
    config = GameConfig()
    rng = SeededRng(seed)
    state = initial_state(config, rng)
    for _ in range(500):
        state = step(state, Intent.NONE, rng)
        assert state.speed <= config.max_speed + 1e-9
        if state.phase is Phase.GAME_OVER:
            break


@settings(max_examples=100)
@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
def test_obstacles_count_invariant(seed):
    config = GameConfig()
    rng = SeededRng(seed)
    state = initial_state(config, rng)
    for _ in range(200):
        state = step(state, Intent.NONE, rng)
        assert len(state.obstacles) == config.lanes


@settings(max_examples=50)
@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
def test_game_over_is_absorbing(seed):
    config = GameConfig()
    rng = SeededRng(seed)
    state = initial_state(config, rng)
    over = replace(state, phase=Phase.GAME_OVER)
    after = step(over, Intent.LEFT, rng)
    assert after is over
