# Análisis del programa original

## Encuadre

- **Programa**: `road_racer.bas`
- **Plataforma canónica**: ZX Spectrum 48K (Sinclair BASIC, 1982-1992)
- **Dialecto**: Sinclair BASIC con tokens completos (`GO TO`, `GO SUB`,
  `PRINT AT`, `INK`, `PAPER`, `BORDER`, `FLASH`, `BEEP`, `INKEY$`).
- **Año estimado**: 1983-1985 (franja de los type-in cortos de
  *Microhobby*, *Crash*, *Your Sinclair*).
- **Género**: arcade — esquivar tráfico en una carretera de 4 carriles.
- **Procedencia exacta**: ver `legacy/SOURCES.md`. Reconstrucción
  representativa (`[LICENCIA CREATIVA]`) inspirada en *Road Racer*
  (Hyperion, 1983).
- **Tamaño**: 70 líneas BASIC.
- **Versión canónica para la reinterpretación**: la única importada.

## Sinopsis funcional

Vista cenital de una carretera vertical con 4 carriles. El jugador
conduce un coche representado por `#` en la fila inferior. Obstáculos
(`@`) bajan desde el borde superior a una velocidad `sp` creciente. El
jugador cambia de carril con `O` (izquierda) y `P` (derecha). Si el
obstáculo de su carril alcanza la fila 19, hay colisión: se pierde
una vida (`lv`), suena un `BEEP` grave y se reinician los obstáculos.
Cada tick suma `sp` puntos (`sc`). Cada 200 puntos sube la velocidad
en 1. Al perder las 3 vidas, aparece `GAME OVER`, se actualiza el
récord `hi` y se vuelve al inicio.

## Lectura crítica

Es un type-in honesto: cabe en un par de columnas de revista,
entiende el problema (un dodge vertical), aplica las técnicas
canónicas (`PRINT AT`, repintado de fotograma completo, BEEP por
evento). Su lógica adolece de las limitaciones esperables:

1. **El repintado es destructivo.** `CLS` cada frame produce parpadeo
   (no usa back-buffer porque Sinclair BASIC no lo soporta de fábrica).
2. **La detección de colisión sólo mira la fila 19** y un único punto
   por carril, no toda la silueta. Si dos obstáculos quedan en
   carriles distintos, sólo el del propio carril cuenta.
3. **El reloj del juego es el propio bucle BASIC**: la velocidad real
   depende de cuánto tarde el intérprete por línea. En máquina real va
   más lento que en emulador moderno.
4. **No hay aceleración del jugador**: se conduce por carriles, no por
   física.

## Grafo de flujo

```
                +----------+
                |  10-30   |  init (border/intro/hi)
                +----+-----+
                     |
                     v
                +----+-----+
                | 100-150  |  reset partida (sc=0,lv=3,sp=4,arrays)
                +----+-----+
                     |
                     v
        +----------> 200 main loop
        |            |
        |   +--------+--------+
        |   | 210 CLS+marco   |
        |   | 220 GOSUB 8000  |  dibuja carretera
        |   | 230 lv==0? --> 5000 GAME OVER
        |   | 240 GOSUB 1000  |  INPUT teclado
        |   | 250 GOSUB 2000  |  mover obstáculos
        |   | 260 GOSUB 3000  |  colisión -> GOSUB 7000
        |   | 270 GOSUB 4000  |  render
        |   | 280 sc+=sp
        |   | 290 sc%200==0? sp++
        |   +-----------------+
        |            |
        +------------+  GO TO 230

  GO SUB 7000 (choque)  -> BEEP, BORDER 2, PAUSE, lv-=1, RESET obstáculos
  GO SUB 9000 (intro)   -> splash + "pulsa una tecla"
  GO SUB 8000 (track)   -> bordes "|" y líneas discontinuas
  5000-5060 (over)      -> CLS, FLASH "GAME OVER", actualiza hi, vuelve a 100
```

## Inventario de variables

| Var | Tipo | Rol                                          |
| --- | ---- | -------------------------------------------- |
| `sc`| num  | puntuación de la partida actual              |
| `hi`| num  | récord acumulado entre partidas              |
| `lv`| num  | vidas restantes (0-3)                        |
| `sp`| num  | velocidad (entera, sube cada 200 pts)        |
| `cl`| num  | carril del jugador (1-4)                     |
| `o(4)`| num| posición vertical del obstáculo por carril   |
| `i`, `y`| num | índices auxiliares                        |
| `k$`| str  | tecla leída por `INKEY$`                     |

## Inventario de subrutinas

| Línea | Nombre interno         | Entradas/Salidas                          |
| ----- | ---------------------- | ----------------------------------------- |
| 1000  | leer teclado           | lee `INKEY$`, muta `cl`                   |
| 2000  | mover obstáculos       | suma `sp/2` a `o(i)`, reciclo aleatorio   |
| 3000  | colisión               | si `o(cl)=19` -> `GO SUB 7000`            |
| 4000  | render                 | dibuja obstáculos, coche, HUD             |
| 5000  | game over              | flash, récord, espera tecla, reinicia     |
| 7000  | rutina de choque       | beep, border, `lv-=1`, reset obstáculos   |
| 8000  | marco de carretera     | dibuja "|" y "." en celdas pares          |
| 9000  | intro                  | título, instrucciones, espera tecla       |

## IO y dispositivos

- **Teclado**: `INKEY$` no bloqueante. Teclas usadas: `O`, `P`.
- **Pantalla**: modo texto 32×24 con atributos por celda; uso de
  `INK 5/6/7/2` para colorear coche, obstáculos, marca de récord.
- **Bordes**: `BORDER 0` normal, `BORDER 2` al chocar (efecto rojo).
- **Sonido**: `BEEP duración, semitono` a través del altavoz del
  Spectrum (no AY-3-8912; la versión 48K no lo lleva).
- **Aleatorio**: `RANDOMIZE` (sin argumento -> usa contador del frame)
  y `RND` para reposicionar obstáculos.
- **Persistencia**: ninguna. `hi` se pierde al apagar.

## Algoritmos identificados y nombrados

1. **Lane dodge loop**: bucle de juego principal sin doble buffer,
   actualiza estado y repinta cada frame.
2. **Vertical wrap respawn**: cuando `o(i) > 20`, se recoloca en
   `-INT(RND*25)-2`, garantizando un margen aleatorio antes de
   reaparecer arriba.
3. **Speed ramp aritmética**: `sp` aumenta en 1 cada 200 puntos, sin
   tope explícito. En el original real esto causaría reactividad
   imposible en ZX 48K real; un bug aceptado de la época.
4. **Mono-carril collision**: la colisión sólo se evalúa contra el
   carril del jugador y a una `y` fija (19). Esto da margen visual.

## Bugs y rarezas

| Línea | Problema                                              | Severidad |
| ----- | ----------------------------------------------------- | --------- |
| 290   | `sc/200=INT(sc/200)` falla si `sp` no divide a 200    | menor     |
| 3010  | `INT(o(cl))=19` puede saltarse si `sp/2` no es entero | medio     |
| 2030  | El reciclo no comprueba solapamiento con otros        | menor     |
| 4030  | Borrar/dibujar sin `OVER 1` produce parpadeo          | estética  |
| —     | Récord `hi` no persiste entre encendidos              | mayor     |

### Bugs corregidos en la versión 2026

- **Colisión por ventana, no por igualdad** (`o(cl) in [19,20]`).
- **Tick determinista**: independiente del tiempo de bucle BASIC.
- **Récord persistente** en JSON (XDG).
- **Doble buffer**: en TUI con Textual no hay parpadeo.
- **Velocidad acotada** con curva de dificultad explícita.

## Sin assembly inline

No hay `DATA` con bytes ni `CALL`/`USR`. Es BASIC puro, lo que lo hace
óptimo para la reinterpretación moderna sin perder fidelidad.
