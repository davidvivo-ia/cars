"""JSON-backed scoreboard repository."""

from __future__ import annotations

import json
from pathlib import Path

from platformdirs import user_data_path
from pydantic import BaseModel, Field, ValidationError

from highway.domain.scoreboard import ScoreEntry

MAX_ENTRIES = 5


class _ScoreEntryModel(BaseModel):
    """Pydantic surface model for serializing a :class:`ScoreEntry`."""

    name: str = Field(min_length=1, max_length=12)
    score: int = Field(ge=0)
    speed: float = Field(ge=0)
    seed: int
    ticks: int = Field(ge=0)


class _ScoreboardModel(BaseModel):
    entries: list[_ScoreEntryModel] = Field(default_factory=list)


def default_scoreboard_path() -> Path:
    """Return the XDG-compliant path for the scoreboard file."""
    return user_data_path("highway", appauthor=False, ensure_exists=True) / "scoreboard.json"


class JsonScoreboard:
    """Persist high scores in a small JSON file under XDG_DATA_HOME."""

    __slots__ = ("path",)

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_scoreboard_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------- Repository API
    def load(self) -> tuple[ScoreEntry, ...]:
        """Return the persisted entries sorted by score desc, ticks asc."""
        return tuple(self._sorted(self._read()))

    def add(self, entry: ScoreEntry) -> tuple[ScoreEntry, ...]:
        """Append *entry* and keep only the top ``MAX_ENTRIES`` records."""
        current = list(self._read())
        current.append(entry)
        keep = self._sorted(current)[:MAX_ENTRIES]
        self._write(keep)
        return tuple(keep)

    # --------------------------------------------------- helpers
    @staticmethod
    def _sorted(items: list[ScoreEntry]) -> list[ScoreEntry]:
        return sorted(items, key=lambda e: (-e.score, e.ticks, e.name))

    def _read(self) -> list[ScoreEntry]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            model = _ScoreboardModel.model_validate(raw)
        except (OSError, json.JSONDecodeError, ValidationError):
            return []
        return [
            ScoreEntry(
                name=m.name,
                score=m.score,
                speed=m.speed,
                seed=m.seed,
                ticks=m.ticks,
            )
            for m in model.entries
        ]

    def _write(self, items: list[ScoreEntry]) -> None:
        model = _ScoreboardModel(
            entries=[
                _ScoreEntryModel(
                    name=e.name,
                    score=e.score,
                    speed=e.speed,
                    seed=e.seed,
                    ticks=e.ticks,
                )
                for e in items
            ]
        )
        self.path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
