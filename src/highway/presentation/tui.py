"""Textual TUI for Road Racer 2026."""

from __future__ import annotations

from importlib.resources import files
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from highway.application import DemoBot, GameLoop
from highway.domain import GameState, Intent
from highway.infrastructure import JsonScoreboard
from highway.presentation.render import render_frame, render_status

CSS_PATH = files("highway.assets").joinpath("highway.tcss")


class PlayfieldWidget(Static):
    """Static widget that re-renders the play field every tick."""

    state: reactive[GameState | None] = reactive(None, recompose=False)

    def watch_state(self, state: GameState | None) -> None:
        if state is None:
            return
        self.update(render_frame(state))


class StatusWidget(Static):
    """Static widget that displays score, lives, speed and record."""

    state: reactive[GameState | None] = reactive(None, recompose=False)
    best: reactive[int] = reactive(0, recompose=False)

    def watch_state(self, state: GameState | None) -> None:
        if state is None:
            return
        self.update(render_status(state, self.best))

    def watch_best(self, _: int) -> None:
        if self.state is not None:
            self.update(render_status(self.state, self.best))


class HighwayApp(App[None]):
    """Top-level Textual application."""

    CSS_PATH: ClassVar[str] = str(CSS_PATH)
    TITLE = "Road Racer 2026"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left,a", "left", "Izq", show=True),
        Binding("right,d", "right", "Der", show=True),
        Binding("space", "pause", "Pausa", show=True),
        Binding("r", "restart", "Reiniciar", show=True),
        Binding("q,escape", "quit", "Salir", show=True),
    ]

    def __init__(
        self,
        loop: GameLoop,
        scoreboard: JsonScoreboard,
        seed: int,
        bot: DemoBot | None = None,
        player_name: str = "PLAYER",
        tick_seconds: float = 0.08,
    ) -> None:
        super().__init__()
        self._game = loop
        self._scoreboard = scoreboard
        self._seed = seed
        self._bot = bot
        self._player_name = player_name
        self._tick_seconds = tick_seconds
        self._pending_intent: Intent = Intent.NONE
        self._paused = False
        self._best_score = max(
            (entry.score for entry in scoreboard.load()),
            default=0,
        )

    # ------------------------------------------------- compose
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical():
            with Center():
                yield PlayfieldWidget(id="playfield")
            yield StatusWidget(id="status-line")
        yield Footer()

    def on_mount(self) -> None:
        playfield = self.query_one("#playfield", PlayfieldWidget)
        status = self.query_one("#status-line", StatusWidget)
        playfield.state = self._game.state
        status.best = self._best_score
        status.state = self._game.state
        self.set_interval(self._tick_seconds, self._tick)

    # ------------------------------------------------- bindings
    def action_left(self) -> None:
        self._pending_intent = Intent.LEFT

    def action_right(self) -> None:
        self._pending_intent = Intent.RIGHT

    def action_pause(self) -> None:
        self._paused = not self._paused

    def action_restart(self) -> None:
        self._game.reset()
        self._paused = False
        self._refresh_widgets()

    # ------------------------------------------------- tick
    def _tick(self) -> None:
        if self._paused or self._game.is_over:
            if self._game.is_over:
                self._finalize_once()
            return
        intent = self._pending_intent
        if self._bot is not None:
            intent = self._bot.decide(self._game.state)
        self._pending_intent = Intent.NONE
        self._game.step(intent)
        self._refresh_widgets()

    def _refresh_widgets(self) -> None:
        playfield = self.query_one("#playfield", PlayfieldWidget)
        status = self.query_one("#status-line", StatusWidget)
        playfield.state = self._game.state
        status.state = self._game.state

    def _finalize_once(self) -> None:
        if getattr(self, "_already_finalized", False):
            return
        self._already_finalized = True
        summary = self._game.finalize(self._player_name, self._seed)
        if summary.new_top_list:
            self._best_score = summary.new_top_list[0].score
            status = self.query_one("#status-line", StatusWidget)
            status.best = self._best_score
        # exit after a short pause so the player sees the final frame
        self.set_timer(1.5, self.exit)
