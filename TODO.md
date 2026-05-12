# TODO — Hoja de ruta hacia v1.1

Backlog priorizado tras la entrega de v1.0.0.

## Alta prioridad

1. **Tabla de power-ups y obstáculos variados** (charcos, motos,
   camiones lentos). Hoy todos los obstáculos comparten silueta y
   velocidad.
2. **Sonido sintetizado** vía `numpy`/`sounddevice` para reproducir un
   `BEEP` AY-3-8912 más cercano al original, manteniendo `NO_BELL=1`.
3. **Modo Contrarreloj** y **Supervivencia**: dos casos de uso ya
   esbozados en el prototipo previo, fáciles de añadir reutilizando el
   reducer.

## Media prioridad

4. **Modo arcoíris**: bandas multicolor del Spectrum como pantalla de
   carga (600 ms al arrancar), ya descrito en `docs/design.md` pero
   pendiente de implementar en el splash de Textual.
5. **Replay determinista**: con el seed y la lista de intents, basta
   serializar los inputs para reproducir partidas.

## Baja prioridad

6. **Selección de coche** con `Cohete`/`Garra`/`Tanque` (stats
   distintos). Pequeño refactor de `GameConfig`.

## Limitaciones conocidas v1.0

- La fuente legacy es una **reconstrucción** ([LICENCIA CREATIVA]); no
  se localizó listado verbatim del *Road Racer* (1983, Hyperion) en
  texto plano. Ver `legacy/SOURCES.md`.
- La TUI no tiene pruebas con `Pilot` aún; cobertura global queda en
  67% por dejar la presentación sin tests automáticos. El dominio sí
  pasa el listón (≥97%).
- En terminales muy estrechas (<24 columnas) la pista se ve recortada.
