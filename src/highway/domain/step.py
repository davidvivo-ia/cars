"""Pure reducer that advances the game one tick."""

from __future__ import annotations

from dataclasses import replace

from highway.domain.config import GameConfig
from highway.domain.errors import InvalidLaneError
from highway.domain.intents import Intent
from highway.domain.rng import Rng
from highway.domain.state import GameState, Obstacle, Phase

# ---------------------------------------------------------------- helpers


def _spawn_obstacle(lane: int, rng: Rng) -> Obstacle:
    """Create a fresh obstacle above the play field for *lane*."""
    # Negative rows mean off-screen above. Spread vertically for variety.
    return Obstacle(lane=lane, row=-1.0 - rng.fraction() * 6.0)


def initial_state(config: GameConfig, rng: Rng) -> GameState:
    """Build a fresh ``GameState`` ready to play.

    Args:
        config: Game tuning.
        rng: Random source for obstacle initial positions.

    Returns:
        A new immutable game state.
    """
    middle = config.lanes // 2 - 1 if config.lanes % 2 == 0 else config.lanes // 2
    obstacles = tuple(_spawn_obstacle(lane, rng) for lane in range(config.lanes))
    return GameState(
        config=config,
        player_lane=middle,
        obstacles=obstacles,
        score=0,
        lives=config.initial_lives,
        speed=config.initial_speed,
        tick=0,
        phase=Phase.PLAYING,
        crash_flash=0,
    )


# ---------------------------------------------------------------- step


def _apply_intent(state: GameState, intent: Intent) -> GameState:
    """Apply an :class:`Intent` to the player lane if it is valid."""
    lanes = state.config.lanes
    lane = state.player_lane
    match intent:
        case Intent.LEFT:
            lane = max(0, lane - 1)
        case Intent.RIGHT:
            lane = min(lanes - 1, lane + 1)
        case Intent.NONE | Intent.PAUSE | Intent.QUIT:
            pass
    if not 0 <= lane < lanes:
        raise InvalidLaneError(lane, lanes)
    return replace(state, player_lane=lane)


def _advance_obstacles(state: GameState, rng: Rng) -> GameState:
    """Move every obstacle down by ``state.speed`` rows and recycle off-screen ones.

    When an obstacle crosses the bottom of the play field, it respawns
    at the top in a randomly chosen lane.
    """
    cfg = state.config
    new_items: list[Obstacle] = []
    for obstacle in state.obstacles:
        next_row = obstacle.row + state.speed
        if next_row > cfg.playfield_height:
            new_lane = rng.integer(0, cfg.lanes - 1)
            new_items.append(_spawn_obstacle(new_lane, rng))
        else:
            new_items.append(replace(obstacle, row=next_row))
    return replace(state, obstacles=tuple(new_items))


def _check_collision(state: GameState, rng: Rng) -> GameState:
    """Detect collisions with the player's lane.

    A collision is recorded when at least one obstacle sits in the
    player's lane and its visible row is inside the collision band.
    Loses a life and recycles the offending obstacles above the screen.
    """
    cfg = state.config
    crashed = False
    new_items: list[Obstacle] = []
    for obstacle in state.obstacles:
        if (
            obstacle.lane == state.player_lane
            and cfg.collision_top <= obstacle.visible_row <= cfg.player_row
        ):
            crashed = True
            new_items.append(_spawn_obstacle(obstacle.lane, rng))
        else:
            new_items.append(obstacle)
    if not crashed:
        return state
    lives = max(0, state.lives - 1)
    phase = Phase.GAME_OVER if lives == 0 else state.phase
    return replace(
        state,
        obstacles=tuple(new_items),
        lives=lives,
        phase=phase,
        crash_flash=6,
    )


def _bump_score_and_speed(state: GameState) -> GameState:
    """Increase score and ramp up speed when the threshold is crossed."""
    cfg = state.config
    score_inc = max(1, round(state.speed * 4))
    new_score = state.score + score_inc
    new_speed = state.speed
    if state.score // cfg.speed_threshold != new_score // cfg.speed_threshold:
        new_speed = min(cfg.max_speed, state.speed + cfg.speed_increment)
    return replace(state, score=new_score, speed=new_speed)


def _decay_flash(state: GameState) -> GameState:
    if state.crash_flash > 0:
        return replace(state, crash_flash=state.crash_flash - 1)
    return state


def step(state: GameState, intent: Intent, rng: Rng) -> GameState:
    """Advance the game one tick.

    The function is pure: same inputs (including RNG state) -> same
    output. The new tick counter is increased by one and the phase
    transitions to ``GAME_OVER`` automatically when lives reach 0.

    Args:
        state: Current immutable game state.
        intent: Player intent for this tick.
        rng: Random source used for obstacle recycling.

    Returns:
        The next immutable game state.
    """
    if state.phase is Phase.GAME_OVER:
        return state
    after_intent = _apply_intent(state, intent)
    after_move = _advance_obstacles(after_intent, rng)
    after_collide = _check_collision(after_move, rng)
    after_score = _bump_score_and_speed(after_collide)
    return replace(_decay_flash(after_score), tick=state.tick + 1)
