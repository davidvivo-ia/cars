"""Tests for the JSON scoreboard repository."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from highway.domain import ScoreEntry
from highway.infrastructure import JsonScoreboard


@pytest.fixture
def scoreboard_path(tmp_path: Path) -> Path:
    return tmp_path / "scoreboard.json"


def test_load_returns_empty_when_no_file(scoreboard_path):
    sb = JsonScoreboard(path=scoreboard_path)
    assert sb.load() == ()


def test_add_persists_and_sorts(scoreboard_path):
    sb = JsonScoreboard(path=scoreboard_path)
    sb.add(ScoreEntry(name="A", score=100, speed=1.0, seed=1, ticks=10))
    sb.add(ScoreEntry(name="B", score=200, speed=2.0, seed=2, ticks=20))
    sb.add(ScoreEntry(name="C", score=150, speed=1.5, seed=3, ticks=15))
    top = sb.load()
    assert [e.name for e in top] == ["B", "C", "A"]


def test_scoreboard_caps_to_five(scoreboard_path):
    sb = JsonScoreboard(path=scoreboard_path)
    for i in range(7):
        sb.add(ScoreEntry(name=f"P{i}", score=i, speed=1.0, seed=i, ticks=i))
    assert len(sb.load()) == 5


def test_scoreboard_recovers_from_corrupt_file(scoreboard_path):
    scoreboard_path.write_text("{not json")
    sb = JsonScoreboard(path=scoreboard_path)
    assert sb.load() == ()
    sb.add(ScoreEntry(name="A", score=1, speed=1.0, seed=1, ticks=1))
    assert len(sb.load()) == 1


def test_scoreboard_validates_entries(scoreboard_path):
    sb = JsonScoreboard(path=scoreboard_path)
    with pytest.raises(ValidationError):
        sb.add(ScoreEntry(name="", score=-1, speed=-1.0, seed=0, ticks=-1))
