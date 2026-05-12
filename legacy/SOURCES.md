# Procedencia del código en `legacy/`

## Encargo

Reinterpretar un programa de los años 80 como obra de software de 2026.
La carpeta del repositorio (`cars`) y la trayectoria de uso indican
**juego de carreras de coches**, con énfasis en esquivar tráfico en una
carretera de varios carriles (mecánica clásica de los listados de la
época).

## Búsqueda realizada (Fase -1)

Se buscó en este orden:

1. `WebSearch` para listados originales de revistas (Microhobby, Crash,
   Your Sinclair, Compute!, Creative Computing) — sólo se localizaron
   referencias bibliográficas, no listados descargables en formato texto.
2. Catálogo de juegos ZX Spectrum *escritos en BASIC*:
   <https://gist.github.com/mrcook/a67e848f7f322131a70e031f5646a567>
3. Candidatos identificados: **Road Racer** (Hyperion Software, 1983,
   242 líneas BASIC) y otros del mismo género. Ficha MobyGames:
   <https://www.mobygames.com/game/75655/road-racer/>
4. Internet Archive y Spectrum Computing publican el programa solo en
   formato binario (`.tap` / `.tzx`); el listado no está expuesto en
   texto plano. `WebFetch` a `archive.org` y `spectrumcomputing.co.uk`
   devolvió `503/403`.
5. Tampoco se localizó listado abierto en GitHub.

Tras seis intentos, se aplica la cláusula de último recurso del
`CLAUDE.md`.

## Decisión [LICENCIA CREATIVA]

`legacy/spectrum/road_racer.bas` es una **reconstrucción** en Sinclair
BASIC idiomático del archetipo de los type-in de coches de revista
española/inglesa de la franja 1983-1985, con el espíritu de *Road Racer*
(Hyperion, 1983) como inspiración funcional:

- 4 carriles dibujados con `PRINT AT`/líneas discontinuas.
- Coche del jugador anclado en la fila inferior, movimiento lateral por
  carril (teclas O/P, las habituales de la época en Sinclair).
- Obstáculos por carril que descienden con velocidad creciente.
- Vidas (`lv`), puntuación (`sc`), velocidad (`sp`) y récord (`hi`).
- `BEEP` para feedback sonoro a través del altavoz interno.
- Estructura `GO SUB`/`GO TO` por bloques numerados a la manera de los
  type-in clásicos.

Se publica como obra de referencia para el ejercicio de arqueología; no
se atribuye autoría al estudio original (Hyperion Software) puesto que
**no es** su listado. La forma, idioms, errores tolerables y limitaciones
son fieles a la época.

## Marcadores de confianza aplicados

- `[DATO]`: tokens BASIC reales del intérprete de Sinclair, paleta INK
  estándar 0-7, modelo 48K.
- `[INFERENCIA]`: convenciones de revista (`O`/`P` para izq/der,
  `pulsa una tecla` para reiniciar) basadas en docenas de listados de
  *Microhobby* y *Crash*.
- `[LICENCIA CREATIVA]`: el listado entero, por lo expuesto arriba.

## Estatus legal

Reconstrucción original publicada bajo la misma licencia que el resto
del repositorio (MIT). No incorpora código de Hyperion Software.
