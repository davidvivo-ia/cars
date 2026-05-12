# Arquitectura

`highway` separa **dominio puro** (lógica del juego), **aplicación** (casos
de uso), **infraestructura** (RNG, persistencia) y **presentación** (TUI
Textual + CLI). Cada capa depende sólo de la siguiente hacia dentro.

```
┌──────────────────────────────────────────────────────────────┐
│                       presentation/                          │
│   TUI Textual · CLI typer · vistas, screens, bindings        │
└───────────────▲──────────────────────────────────────────────┘
                │ usa
┌───────────────┴──────────────────────────────────────────────┐
│                       application/                           │
│   GameLoop · DemoBot · ScoreService                          │
└───────────────▲──────────────────────────────────────────────┘
                │ usa
┌───────────────┴──────────────────────────────────────────────┐
│                       infrastructure/                        │
│   SeededRng · JsonScoreboard (XDG) · ClockTicker             │
└───────────────▲──────────────────────────────────────────────┘
                │ usa
┌───────────────┴──────────────────────────────────────────────┐
│                          domain/                             │
│   Lane · Car · Obstacle · GameState · step() (pure)          │
│   value objects frozen+slots · sin IO · sin globals          │
└──────────────────────────────────────────────────────────────┘
```

## Reglas

1. `domain/` no importa nada de `application/`, `infrastructure/` o
   `presentation/`.
2. `application/` no importa `presentation/`.
3. RNG y reloj se **inyectan** desde `infrastructure/` mediante
   protocolos (Protocol/ABC) declarados en `domain/`.
4. Persistencia (high scores) se aborda a través de un repositorio
   declarado en `domain/` e implementado en `infrastructure/`.
5. Dominio puramente funcional: la función `step(state, intent, rng)`
   devuelve un `GameState` nuevo. Cero mutación.

## Composición en runtime

```
typer CLI ── builds ─▶ Textual App
                         │
                         ▼
                     GameLoop ── tick(state, intent, rng) ──▶ new state
                         │                                       ▲
                         │                                       │
            ScoreService.save() ◀── on GameOver ──── new high?  │
                         │                                       │
            JsonScoreboard.persist() ────────────────────────────┘
```

## Ciclo de vida de un frame

1. Textual emite un evento `Tick` (cada ~16 ms).
2. `GameApp` recoge la `Intent` actual del jugador (carril izq/der, sin
   acción) y la pasa al `GameLoop`.
3. `GameLoop.step()` invoca `domain.step()` con el `GameState`
   inmutable actual + RNG inyectado.
4. Se renderiza el nuevo estado a través de los widgets.

El `DemoBot` reemplaza al jugador humano: produce intents
deterministas dado un seed, sin renderizar nada (modo `--demo --headless`)
o renderizando normalmente (modo `--demo` con UI).

## Dependencias externas autorizadas

- `typer` (CLI), `rich` (formateo de comandos `--help`).
- `textual` (TUI).
- `pydantic v2` solo en la frontera de configuración y persistencia.
- `structlog` para logging interno (rich render dev / JSON prod).
- `pytest` + `hypothesis` en tests.
- `ruff`, `mypy` para calidad.

Dominio sin dependencias salvo stdlib.
