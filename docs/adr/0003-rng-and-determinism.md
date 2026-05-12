# ADR 0003 — RNG inyectado y determinismo

## Contexto

El original llama a `RND` directamente. Queremos:

- `--seed <int>` para partidas reproducibles.
- `--demo` que termine siempre igual con un seed dado.
- Tests deterministas.

## Decisión

Un `Protocol` `Rng` declarado en `domain/`:

```python
class Rng(Protocol):
    def integer(self, low: int, high: int) -> int: ...
    def fraction(self) -> float: ...
```

Implementación por defecto en `infrastructure/rng.py` envolviendo
`random.Random(seed)`. El dominio jamás llama a `random` directamente.

## Consecuencias

- Tests pueden pasar un `Rng` falso/estático.
- El `--demo` carga seed fijo (42 por defecto).
- En producción el seed por defecto viene de `time.time_ns()`.
