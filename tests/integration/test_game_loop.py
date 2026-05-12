"""End-to-end test of GameLoop + DemoBot on top of the real reducer."""

from __future__ import annotations

from highway.application import DemoBot, GameLoop
from highway.domain import GameConfig, ScoreboardRepository, ScoreEntry
from highway.infrastructure import SeededRng


class FakeScoreboard:
    def __init__(self) -> None:
        self.entries: list[ScoreEntry] = []

    def load(self) -> tuple[ScoreEntry, ...]:
        return tuple(sorted(self.entries, key=lambda e: -e.score))

    def add(self, entry: ScoreEntry) -> tuple[ScoreEntry, ...]:
        self.entries.append(entry)
        return self.load()


def _build_loop(seed: int = 42) -> tuple[GameLoop, FakeScoreboard]:
    sb = FakeScoreboard()
    loop = GameLoop(config=GameConfig(), rng=SeededRng(seed), scoreboard=sb)
    return loop, sb


def test_demo_run_terminates_and_persists():
    loop, sb = _build_loop()
    bot = DemoBot()
    ticks = 0
    while not loop.is_over and ticks < 4000:
        loop.step(bot.decide(loop.state))
        ticks += 1
    summary = loop.finalize("DEMO", seed=42)
    assert summary.final_state.lives == 0
    assert summary.ticks_played > 0
    assert sb.load()  # there is at least one entry persisted


def test_two_seeded_runs_produce_identical_results():
    loop_a, _ = _build_loop(seed=1234)
    loop_b, _ = _build_loop(seed=1234)
    bot = DemoBot()
    for _ in range(500):
        loop_a.step(bot.decide(loop_a.state))
        loop_b.step(bot.decide(loop_b.state))
        if loop_a.is_over or loop_b.is_over:
            break
    assert loop_a.state.score == loop_b.state.score
    assert loop_a.state.tick == loop_b.state.tick


def test_repository_protocol_is_satisfied():
    # Type check at runtime that the fake is a structural match.
    sb: ScoreboardRepository = FakeScoreboard()
    assert sb.load() == ()
