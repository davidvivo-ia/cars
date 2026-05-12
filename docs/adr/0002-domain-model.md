# ADR 0002 — Modelo de dominio inmutable

## Contexto

El BASIC original mantiene estado como variables globales (`sc`, `lv`,
`sp`, `cl`, `o(4)`). Para 2026 queremos un dominio testeable sin mocks,
con `mypy --strict` y propiedad verificable con `hypothesis`.

## Opciones

1. **Dataclasses mutables**: simples pero invitan a errores y rompen
   testabilidad funcional.
2. **`@dataclass(frozen=True, slots=True)` + función pura `step()`**:
   estado nuevo cada tick, RNG inyectado.
3. **Clases con métodos `update()` mutables**: cómodo pero acopla
   secuenciado y deja huecos para tests.

## Decisión

**Opción 2**: dataclasses frozen + función pura. El reducer es
`step(state, intent, rng) -> state`. El `GameLoop` lo invoca cada
tick.

## Consecuencias

- Cero estado compartido implícito.
- Cada tick es trivialmente serializable (útil para replay/--demo).
- Mayor presión sobre las construcciones (cada `replace` genera un
  objeto nuevo), pero el `slots=True` lo hace barato en CPython 3.13.
- `hypothesis` puede generar `GameState` fácilmente.
