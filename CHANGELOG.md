# Changelog

Sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y
[Semantic Versioning](https://semver.org/lang/es/spec/v2.0.0.html).

## [1.0.0] - 2026-05-12

### Preservado del original

- Mecánica de **lane dodge vertical** sobre carretera de 4 carriles.
- Coche del jugador anclado en la fila inferior, control por carril
  con teclas (mapeo "O/P" del original adaptado a flechas y A/D).
- Tres vidas, puntuación monotónica, velocidad creciente cada 200
  puntos, récord en pantalla.
- Tabla de obstáculos por carril que reciclan al salir por abajo.
- Estética inspirada en la paleta BRIGHT 1 del ZX Spectrum y campanita
  ANSI como guiño al `BEEP` del altavoz original.

### Modernizado

- Reimplementación íntegra en **Python 3.13** con `mypy --strict`,
  `ruff` y `pre-commit`.
- Arquitectura por capas (**domain / application / infrastructure /
  presentation**) con dominio puro e inmutable
  (`@dataclass(frozen=True, slots=True)`).
- Reducer puro `step(state, intent, rng)` testeable sin mocks.
- **TUI con Textual**: rejilla 22×16 con doble buffer (sin parpadeo),
  bindings de teclado declarativos, hoja de estilos `highway.tcss`.
- Persistencia de récords en XDG_DATA_HOME usando **pydantic v2**.
- RNG inyectado (`SeededRng`) que habilita `--seed` y partidas
  reproducibles.

### Añadido

- Subcomando `highway scores` para inspeccionar el top-5 persistido.
- Modo `--demo` con `DemoBot` determinista.
- Modo `--demo --headless --max-ticks N` para CI y capturas.
- Tests unitarios (43) y propiedades con `hypothesis`, cobertura del
  dominio ≥97%.
- ADRs (5), `architecture.md`, `design.md`, `original_program_analysis.md`,
  `postmortem.md`.

### Licencias creativas tomadas

- El listado en `legacy/spectrum/road_racer.bas` es una reconstrucción
  representativa de un type-in de revista de la franja 1983-1985 (ver
  `legacy/SOURCES.md`). No es el código verbatim del *Road Racer*
  comercial de Hyperion Software.
- Cambio de teclas: `O`/`P` del original sustituidas por flechas/`A`/`D`
  por accesibilidad moderna.
- Curva de velocidad re-calibrada a unidades por tick deterministas
  (`speed_increment=0.1`, `max_speed=2.5`) en lugar del incremento
  entero del original.

### Bugs corregidos

- Colisión por ventana de filas `[collision_top, player_row]` en lugar
  de igualdad estricta a fila 19 (no se saltaba por velocidades altas).
- Tick desacoplado del tiempo del intérprete: en el original el bucle
  BASIC marcaba el tempo; aquí lo marca un `set_interval` de Textual.
- Récord persistente entre ejecuciones (el original lo perdía al
  apagar la máquina).
