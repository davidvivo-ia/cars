"""Typer CLI for Road Racer 2026."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from highway.application import DemoBot, GameLoop
from highway.domain import GameConfig, Intent
from highway.infrastructure import JsonScoreboard, SeededRng
from highway.presentation.render import render_frame, render_status

app = typer.Typer(
    help="Road Racer 2026 — recreación moderna de un type-in BASIC de ZX Spectrum.",
    add_completion=False,
)
_console = Console()


def _make_scoreboard() -> JsonScoreboard:
    return JsonScoreboard()


def _run_headless(seed: int, max_ticks: int, console: Console) -> int:
    """Run a demo without launching the Textual UI; useful for CI."""
    rng = SeededRng(seed)
    config = GameConfig()
    loop = GameLoop(config=config, rng=rng, scoreboard=_make_scoreboard())
    bot = DemoBot()

    ticks = 0
    while not loop.is_over and ticks < max_ticks:
        loop.step(bot.decide(loop.state))
        ticks += 1

    summary = loop.finalize("DEMO", seed=seed)
    state = summary.final_state
    console.print(render_frame(state))
    console.print(render_status(state, best_score=summary.new_top_list[0].score))
    console.print(
        Panel.fit(
            f"[bold #ffcc00]Resumen demo[/]\n"
            f"Ticks jugados: [bold]{ticks}[/]\n"
            f"Puntuación final: [bold]{state.score}[/]\n"
            f"Seed: [bold]{seed}[/]",
            border_style="#33ff66",
            title="DEMO",
        )
    )
    return 0


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    seed: Annotated[
        int | None,
        typer.Option(help="Semilla para reproducibilidad."),
    ] = None,
    demo: Annotated[
        bool,
        typer.Option("--demo", help="Reproducir una partida automática con DemoBot."),
    ] = False,
    headless: Annotated[
        bool,
        typer.Option("--headless", help="Ejecutar sin TUI, útil para CI."),
    ] = False,
    max_ticks: Annotated[
        int,
        typer.Option(help="Tope de ticks para modo headless."),
    ] = 1500,
) -> None:
    """Entry point of the Highway CLI.

    Sin opciones lanza la TUI de Textual con jugador humano. Con
    ``--demo`` introduce un bot determinista. Con ``--headless`` además
    omite la interfaz textual (uso en CI/tests).
    """
    if ctx.invoked_subcommand is not None:
        return
    actual_seed: int
    if seed is None:
        rng = SeededRng()
        actual_seed = rng.seed
    else:
        rng = SeededRng(seed)
        actual_seed = seed

    if demo and headless:
        sys.exit(_run_headless(actual_seed, max_ticks=max_ticks, console=_console))

    # Full TUI mode (with or without bot).
    from highway.presentation.tui import HighwayApp  # noqa: PLC0415 — lazy load TUI

    config = GameConfig()
    loop = GameLoop(config=config, rng=rng, scoreboard=_make_scoreboard())
    bot: DemoBot | None = DemoBot() if demo else None
    HighwayApp(
        loop=loop,
        scoreboard=_make_scoreboard(),
        seed=actual_seed,
        bot=bot,
        player_name="DEMO" if demo else "PLAYER",
    ).run()


@app.command()
def scores() -> None:
    """Show the persisted top-5 scoreboard."""
    sb = _make_scoreboard()
    entries = sb.load()
    if not entries:
        _console.print("[muted]No hay récords todavía. Juega una partida.[/]")
        return
    _console.print("[bold #ffcc00]Top-5 Road Racer 2026[/]\n")
    for index, entry in enumerate(entries, start=1):
        _console.print(
            f"{index:>2}. {entry.name:<12} {entry.score:>6}  "
            f"velocidad {entry.speed:>4.2f}  seed {entry.seed}",
            style="#f4f4f5",
        )


# `Intent` is used only via TUI/CLI imports; reference it here so that
# `mypy --strict` does not flag an unused import after collapsing imports.
_ = Intent
