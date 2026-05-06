"""Persistencia de mejores marcas en un JSON local."""
import json
import os
from typing import Optional

from config import HIGHSCORE_FILE


def _empty():
    return {
        "Carrera": {"best_distance": 0, "best_time": None},
        "Contrarreloj": {"best_distance": 0},
        "Supervivencia": {"best_distance": 0, "best_time": 0},
    }


def load() -> dict:
    if not os.path.exists(HIGHSCORE_FILE):
        return _empty()
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Rellena modos que falten
        base = _empty()
        for mode, fields in base.items():
            data.setdefault(mode, fields)
        return data
    except (OSError, ValueError):
        return _empty()


def save(data: dict) -> None:
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def update_for_run(data: dict, mode: str, distance: float,
                   time_s: Optional[float] = None) -> bool:
    """Actualiza la entrada del modo si la marca es mejor. Devuelve True si lo es."""
    entry = data.setdefault(mode, {})
    improved = False
    best_dist = entry.get("best_distance", 0)
    if distance > best_dist:
        entry["best_distance"] = float(distance)
        improved = True
    if time_s is not None:
        if mode == "Carrera":
            best_time = entry.get("best_time")
            if best_time is None or time_s < best_time:
                entry["best_time"] = float(time_s)
                improved = True
        elif mode == "Supervivencia":
            best_time = entry.get("best_time", 0)
            if time_s > best_time:
                entry["best_time"] = float(time_s)
                improved = True
    return improved
