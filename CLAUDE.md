# CLAUDE.md

## Misión

Tomar un programa de los años 80 (BASIC ZX Spectrum, Amstrad CPC, Sega
Mega Drive/Genesis, Commodore 64, MSX, Apple II, IBM PC, etc.) y
reconstruirlo como obra de software de 2026: juego completo, jugable,
empaquetado, testeado, documentado y con diseño visual cuidado.

Preservas la lógica funcional y el "alma" del original. Reimaginas todo
lo demás.

No es traducción línea a línea. Es reinterpretación con criterio de
ingeniero senior y sensibilidad de diseñador.

## Obtención del código original (FASE -1)

Antes de cualquier otra cosa, comprueba si `legacy/` contiene código
fuente.

### Caso A: `legacy/` ya tiene código
Procede directamente a la Fase 0.

### Caso B: `legacy/` está vacío o solo contiene una nota del usuario
La nota indicará el juego o tipo de programa que quiero recrear (ej.
"Manic Miner", "Jet Set Willy", "un juego de aventura conversacional tipo
Adventure", "un Frogger", "un Wizard's Castle"). Búscalo tú.

Tu trabajo es **encontrar código fuente real de los años 80** del
programa pedido, o de uno equivalente del mismo género y plataforma, y
copiarlo a `legacy/` antes de empezar.

**Plataformas objetivo, en orden de preferencia:**

1. **ZX Spectrum** (Sinclair BASIC, Z80 assembly).
2. **Amstrad CPC** (Locomotive BASIC, Z80).
3. **Commodore 64** (CBM BASIC v2, 6502).
4. **MSX** (MSX BASIC, Z80).
5. **Apple II** (Applesoft BASIC, Integer BASIC, 6502).
6. **IBM PC** (GW-BASIC, BASICA, Turbo Pascal, C).
7. **Sega Mega Drive / Genesis** (68000 assembly, C con SGDK).
8. **Atari 800 / ST**, **BBC Micro**, **Dragon 32**, **TI-99/4A** si procede.

Si tras búsqueda razonable no encuentras nada utilizable, recurre como
último recurso a un clásico de dominio público de *BASIC Computer Games*
(David Ahl, 1978) o *More BASIC Computer Games* (1979) y documenta la
sustitución.

## Modo de operación: AUTÓNOMO

Trabajas sin pedir permiso. No haces preguntas. Tomas decisiones, las
documentas en ADRs y sigues.

NO PARAS hasta que:

- `uv sync` funcione sin errores.
- `ruff check` esté limpio.
- `ruff format --check` esté limpio.
- `mypy --strict src` pase sin errores.
- `pytest` pase todos los tests con cobertura >=80% en `domain/`.
- El juego sea ejecutable con `uv run <paquete>` y jugable de principio
  a fin.
- Exista un modo `--demo` determinista que complete una partida sin
  intervención humana.
- README, CHANGELOG y los tres documentos de `docs/` estén escritos.

## Stack obligatorio

- Python 3.13+.
- `uv` + `pyproject.toml` (PEP 621), `src/` layout.
- `pydantic` v2 en fronteras IO/config; `dataclass(frozen=True,
  slots=True)` en dominio.
- CLI: `typer` + `rich`.
- TUI: `textual` con CSS propio.
- Gráfico (si procede): `pygame-ce`.
- Logging: `structlog`.
- Tests: `pytest` + `hypothesis`.
- Calidad: `ruff`, `mypy --strict`, `pre-commit`.
- CI: GitHub Actions.

## Estructura

```
src/<paquete>/
├── domain/
├── application/
├── infrastructure/
├── presentation/
└── assets/
tests/{unit,integration,property}/
docs/{architecture,design,original_program_analysis,postmortem}.md
docs/adr/
legacy/
```

## Filosofía

Mejor una v1.0 modesta pero terminada que una v0.7 ambiciosa abandonada.

Empieza por la Fase -1 (o Fase 0 si ya hay código). No respondas pidiendo
confirmación. Pónte a trabajar.
