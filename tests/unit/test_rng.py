"""Tests for SeededRng determinism."""

from __future__ import annotations

from highway.infrastructure import SeededRng


def test_same_seed_yields_same_sequence():
    a = SeededRng(seed=123)
    b = SeededRng(seed=123)
    seq_a = [a.integer(0, 100) for _ in range(20)]
    seq_b = [b.integer(0, 100) for _ in range(20)]
    assert seq_a == seq_b


def test_fraction_returns_in_unit_interval():
    rng = SeededRng(seed=7)
    for _ in range(100):
        v = rng.fraction()
        assert 0.0 <= v < 1.0


def test_unseeded_records_a_seed():
    rng = SeededRng()
    assert isinstance(rng.seed, int)
