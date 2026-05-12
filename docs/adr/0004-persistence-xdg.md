# ADR 0004 — Persistencia de récords con XDG y pydantic

## Contexto

El listado BASIC pierde el récord al apagar. Para 2026 queremos
récords persistentes pero sin acoplar al dominio una librería de IO.

## Decisión

- Modelo `Scoreboard` y `ScoreEntry` con `pydantic v2` en
  `infrastructure/scoreboard.py`.
- Ruta de persistencia: `XDG_DATA_HOME` o, en su defecto,
  `~/.local/share/highway/scoreboard.json`.
- `Protocol` en `domain/repository.py` (`ScoreboardRepository`) para
  inversión de dependencia.

## Consecuencias

- El dominio puede simular el repositorio con un fake en memoria.
- Si el archivo está corrupto, se reinicializa con aviso (sin perder
  partidas futuras).
