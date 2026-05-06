# Carreras 4 Carriles (Python + pygame)

Juego arcade de carreras 2D con 4 carriles, IA, power-ups, modos y récords.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python cars.py
```

## Tests

```bash
python -m unittest discover -s tests
```

## Cómo se juega

- **Jugador 1 (rojo)**: flechas — `←/→` cambiar de carril, `↑` acelerar, `↓` frenar.
- **CPU (azul)**: lo conduce la IA con dificultad ajustable.
- `P` pausa, `R` reiniciar la carrera, `Esc` volver al menú o salir.
- Coge los power-ups para conseguir ventaja, esquiva el tráfico y suma combos.

## Características

- **3 modos**: Carrera (a 3000 m), Contrarreloj (60 s) y Supervivencia.
- **3 dificultades** (Fácil/Normal/Difícil) que cambian la densidad del tráfico, la velocidad y el comportamiento de la IA.
- **3 coches seleccionables** con stats distintos (Cohete, Garra, Tanque).
- **Sistema de vidas** con 3 corazones, invulnerabilidad temporal y rebote tras chocar.
- **Power-ups**: turbo, escudo y aceite (lanzado al rival).
- **Combo de adelantamientos** sin chocar.
- **IA mejorada** con rubber-banding suave para mantener la tensión.
- **Tres tramos visuales** que se alternan: día, anochecer y noche con estrellas.
- **Carretera con curvas** suaves y postes laterales en parallax.
- **Efectos**: humo del tubo de escape, chispas al chocar, líneas de velocidad, screen shake y flash al impactar.
- **Mini-mapa** con la posición del rival.
- **Cuenta atrás 3-2-1-¡YA!** al empezar.
- **Sonidos sintetizados** sin assets externos (turbo, escudo, choque, meta, combo).
- **Mejores marcas** persistentes en `highscore.json`.

## Estructura

```
cars.py            entry point
config.py          tunables (W/H, dificultades, temas, coches, modos…)
entities.py        Car, TrafficCar, PowerUp, ParticleSystem
ai.py              AIDriver con dificultad y rubber-banding
audio.py           sonidos sintetizados
highscore.py       lectura/escritura de records
ui.py              dibujo (carretera, HUD, mini-mapa, menús, overlays)
game.py            máquina de estados y bucle principal
tests/             tests unitarios (sin pantalla)
```
