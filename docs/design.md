# Sistema de diseño

## Concepto

Un type-in de 1983 ejecutándose dentro de una cabina de juegos con
display moderno: fidelidad mecánica, presentación pulcra.

## Paleta

Homenaje a la paleta ZX Spectrum (BRIGHT 1) limpiada para WCAG AA en
fondo oscuro.

| Rol           | Nombre          | Hex       | Uso                                    |
| ------------- | --------------- | --------- | -------------------------------------- |
| `background`  | Asfalto         | `#0e1014` | Fondo principal (carretera, app)       |
| `surface`     | Carril          | `#1a1d24` | Cards, panel info                      |
| `muted`       | Marca lateral   | `#3a3f4a` | Bordes, texto secundario, líneas       |
| `primary`     | Pista           | `#f4f4f5` | Texto principal, líneas discontinuas   |
| `accent`      | Ámbar Spectrum  | `#ffcc00` | Foco, score, FLASH del original        |
| `success`     | Verde 7         | `#33ff66` | Récord, ganador, indicadores OK        |
| `warning`     | Naranja         | `#ff8a3d` | Velocidad alta, vidas bajas            |
| `error`       | Rojo Spectrum   | `#ff3344` | Colisión, game over, vidas perdidas    |

Contraste:
- `primary` sobre `background` = 16.4:1 (AAA).
- `accent` sobre `background` = 11.8:1 (AAA).
- `error` sobre `background` = 5.6:1 (AA).

## Tipografía

- **UI**: `IBM Plex Mono` (presente en muchos sistemas) con fallback al
  monospace por defecto de la terminal. Textual hereda la fuente del
  emulador.
- **Tamaños**: relativos por filas/columnas de carácter; Textual escala
  con la terminal. Headings con `bold`.
- **Pesos**: regular para texto, bold para titulares y HUD.

## Glifos del juego

Aplicamos pixel-art ASCII fiel al original, ampliado para terminales
modernas:

```
Coche jugador:    ┌─┐    Obstáculo:   ╭─╮
                  │█│                 ║▓║
                  └─┘                 ╰─╯
```

- Carril: `┃` con marcas discontinuas `┊` cada 2 filas.
- Carretera: el área central; césped y arcenes con `░`.

## Espaciado

Sistema 1ch / 1 row. Padding estándar de 1, márgenes de 2 entre
secciones. La pista interior es 17 columnas (4 carriles de 4 columnas
más separadores) y 22 filas de alto, replicando el aspect ratio del
ZX Spectrum.

## Iconografía y microinteracciones

- Vidas: `❤  ❤  ❤` (color `error`).
- Combo / velocidad: barra ASCII `▓▓▓░░`.
- Game over: parpadeo lento (1 Hz) en `accent` durante 2 s, luego fijo
  en `error`.
- Beep de evento: opcional via `print('\a')` (campanita ANSI) cuando se
  cambia de carril, choque, récord.

## Estados clave

1. **Splash**: título "ROAD RACER 2026", subtítulo en `muted`, hint
   "Pulsa ENTER para empezar". Cita del listado original en pie.
2. **Game**: pista central, HUD lateral con puntos/vidas/velocidad/récord.
3. **Game over**: overlay semitransparente con resultado, opciones
   "REINTENTAR (R)" / "MENU (ENTER)" / "SALIR (Q)".
4. **High scores**: top-5 con seed de cada partida y modo (humano/demo).
5. **Demo**: igual a Game pero con la badge "DEMO" en `accent` arriba
   a la derecha. No acepta input del jugador.

## Accesibilidad

- Navegación completa por teclado. Mapas declarados en `BINDINGS` de
  cada Screen.
- No depender sólo del color: la colisión cambia color **y** muestra
  flash + sonido + texto.
- Modo `--no-color` simple a través de la variable de entorno
  `NO_COLOR` que Textual respeta.
- Texto siempre >=1ch y nunca encima de cambios de color críticos.

## Toque distintivo memorable

**Beep PC-speaker reinterpretado en consola** vía secuencias ANSI:
cada evento del juego produce una "campanita" (`'\a'`). Y la
pantalla de carga inicial dibuja, durante 600 ms, las **bandas
multicolor** clásicas del Spectrum cargando una cinta. Un homenaje
breve, no intrusivo.

## Bindings

| Tecla         | Acción                      | Pantalla     |
| ------------- | --------------------------- | ------------ |
| ←, A          | Cambiar a carril izquierdo  | Game         |
| →, D          | Cambiar a carril derecho    | Game         |
| Espacio       | Pausa / continuar           | Game         |
| Q             | Salir                       | global       |
| Enter         | Confirmar / nueva partida   | Splash/GO    |
| R             | Reintentar                  | Game over    |
| H             | Ver top-5                   | Splash       |
