# Road Racer 2026

> Reinterpretación moderna de un type-in BASIC de ZX Spectrum (1983) como
> aplicación Python 3.13 con TUI, dominio puro, tests y `--demo`
> reproducible.

```
        ┌──────────┐
        │ ROAD     │
        │ RACER    │
        │ 2026     │
        └──────────┘

  ░░│                │░░
  ░░│   ▲            │░░    ← jugador
  ░░│        █       │░░    ← obstáculo
  ░░│                │░░
  ░░│┊      ┊      ┊ │░░    ← líneas de carril
   PT  1234   VID ♥♥♥   VEL 1.20   REC 5000
```

## Instalación

```bash
uv sync --all-extras
```

## Ejecutar

```bash
uv run highway                    # TUI con jugador humano
uv run highway --demo              # TUI con bot determinista
uv run highway --demo --seed 42 --headless --max-ticks 200   # CI
uv run highway scores              # ver el top-5 persistido
```

## Controles

| Tecla            | Acción                |
| ---------------- | --------------------- |
| ← / A            | Carril a la izquierda |
| → / D            | Carril a la derecha   |
| Espacio          | Pausa / continuar     |
| R                | Reiniciar             |
| Q / Esc          | Salir                 |

## Calidad

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
```

## Procedencia

Reinterpretación de `legacy/spectrum/road_racer.bas`, un type-in
Sinclair BASIC de los 80. Ver:

- `legacy/SOURCES.md` para la procedencia.
- `docs/original_program_analysis.md` para el encuadre/arqueología.
- `docs/architecture.md` para la arquitectura por capas.
- `docs/design.md` para el sistema de diseño visual.
- `docs/adr/` para las ADRs.
- `docs/postmortem.md` tras la entrega.

## Licencia

MIT. Ver `LICENSE`.
