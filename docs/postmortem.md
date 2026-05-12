# Postmortem — Road Racer 2026

Cuarenta años separan el type-in original de esta versión. En 1983 un
chaval con un ZX Spectrum 48K teclaba 70 líneas BASIC desde una revista
y al rato tenía su coche evitando obstáculos: cabía en 16 KB y vivía
mientras el ordenador estuviese encendido. La cinta era el medio, el
parpadeo era el coste de un bucle sin doble buffer, y el récord moría
con el corte de luz. Esa economía radical fue lo que se ganó: cero
fricciones, cero ceremonias, mecánica al alcance de la mano.

Lo que se ha **conservado**: la silueta del juego (4 carriles, esquivar
y subir velocidad), su ritmo simple, su lectura "1 carril = 1
decisión", y un guiño visual a la paleta del Spectrum. La mecánica es
la misma; los carros son los mismos; el reto es el mismo.

Lo que se ha **ganado** en 40 años: tipado estricto (`mypy --strict`),
dominio puro inmutable testeable sin mocks, RNG inyectado para
partidas reproducibles, una TUI moderna sin parpadeo, persistencia
XDG, modo `--demo` determinista, CI con matriz, separación por capas,
43 tests (incluyendo propiedades con `hypothesis`). En 1983 nada de
esto existía como hábito: en 2026 es lo mínimo defendible.

Lo que se ha **perdido**: la inmediatez. Aquel programa cabía en una
revista; éste lleva 13 archivos de código, un `pyproject.toml` y un
flujo de instalación con `uv`. La hospitalidad del "RUN" se ha
sustituido por el rito moderno del `uv sync`. También se pierde el
calor analógico del altavoz cuadrado del Spectrum; el bell ANSI es un
homenaje pero no un sustituto.

Lo que este ejercicio dice sobre cómo ha cambiado el oficio: hemos
acumulado 40 años de experiencia para que el código sea más legible,
verificable y mantenible. Es mejor ingeniería, sin duda. Pero el
ingenio del type-in — un compromiso brutal entre simplicidad y
diversión — no ha quedado obsoleto, sólo cubierto. Bajo las capas, el
reducer puro `step()` de 100 líneas es, esencialmente, el bucle de
1983 con mejor educación. La cosa que importa, "esquivar el de tu
carril", sigue cabiendo en un sólo párrafo.
