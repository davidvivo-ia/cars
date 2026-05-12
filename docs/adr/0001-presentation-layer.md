# ADR 0001 — Capa de presentación

## Contexto

El programa original es un type-in de Sinclair BASIC que dibuja con
`PRINT AT` sobre el modo texto del Spectrum (32×24 con atributos por
celda). El movimiento es por carriles, no píxel a píxel; no usa sprites
ni colisión píxel.

`CLAUDE.md` establece como default **TUI con Textual** cuando el original
es texto/semigráfico y `pygame-ce` cuando hay sprites o scroll píxel
real.

## Opciones consideradas

1. **TUI con Textual.** Mantiene la esencia del original (rejilla,
   colores por celda, glifos), aporta layout moderno, CSS, screens.
2. **pygame-ce.** Permitiría un homenaje pixel-perfect con sprites 8×8,
   pero no aporta nada que la rejilla terminal no resuelva y triplica el
   trabajo de assets.
3. **Rich plano en terminal.** Más simple pero sin event loop ni
   bindings de teclado de calidad para un juego en tiempo real.

## Decisión

**Textual.** Es coherente con la naturaleza char-grid del original y
con la prioridad del proyecto: entregar terminado, jugable y bonito.

## Consecuencias

- Sin overhead de assets gráficos: sprites = caracteres Unicode.
- Reloj del juego = `set_interval` de Textual.
- Tests de presentación posibles vía `Pilot` de Textual.
- Pierde el "calor" del beep AY-3-8912 — se mitiga con el bell ANSI.
