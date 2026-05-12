# ADR 0005 — Estética fusión retro-moderna

## Contexto

`CLAUDE.md` exige un "toque distintivo memorable". El original es ZX
Spectrum BASIC, lo natural es homenajear su identidad visual sin caer
en imitación literal.

## Decisión

Fusión moderna-retro con tres concesiones específicas al original:

1. **Pantalla de carga** que reproduce las bandas multicolor del
   Spectrum durante 600 ms al arrancar la app.
2. **Paleta** basada en los 8 colores BRIGHT 1 del Spectrum, ajustada
   para contraste AA en terminales modernas.
3. **Beep de campanita ANSI** (`\a`) por evento clave (cambio de
   carril, colisión, récord). Reemplazo digno del `BEEP` AY del
   original.

Todo lo demás se diseña con criterio 2026: layout limpio, tipografía
monospace agradable, sin scanlines artificiales (que en TUI son ruido).

## Consecuencias

- Identidad visual reconocible en 1 s.
- Cero dependencia de fuentes externas para que arranque sin assets.
- El bell ANSI se puede silenciar con la variable de entorno
  `NO_BELL=1`.
