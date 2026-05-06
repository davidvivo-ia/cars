"""Constantes y ajustes del juego."""
import os

# ----------------------------------------------------------------- ventana
W, H = 640, 800
FPS = 60

# ----------------------------------------------------------------- carretera
LANES = 4
ROAD_LEFT = 80
ROAD_RIGHT = W - 80
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH / LANES


def lane_center(i: int) -> float:
    return ROAD_LEFT + LANE_WIDTH * (i + 0.5)


# ----------------------------------------------------------------- coches
CAR_W, CAR_H = 38, 64
PLAYER_BASE_Y = H - 140

# ----------------------------------------------------------------- carrera
FINISH_DISTANCE = 3000
MAX_LIVES = 3
INVULN_AFTER_HIT = 70  # frames de invulnerabilidad tras un golpe

# ----------------------------------------------------------------- archivos
ROOT = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(ROOT, "highscore.json")

# ----------------------------------------------------------------- colores
TEXT = (235, 235, 235)
SUBTEXT = (160, 160, 160)
RED = (255, 80, 80)
BLUE = (80, 168, 255)
YELLOW = (255, 220, 100)
GREEN = (110, 220, 130)
PURPLE = (200, 120, 255)
CYAN = (90, 220, 220)
ORANGE = (255, 140, 40)

TRAFFIC_COLORS = [
    (224, 192, 64),
    (154, 74, 214),
    (63, 191, 111),
    (217, 107, 31),
    (204, 204, 204),
]

# ----------------------------------------------------------------- temas
# Cada tema cubre un tramo de la carretera y cambia los colores de fondo.
THEMES = [
    dict(name="Día",     grass=(31, 94, 42),  road=(48, 48, 50), line=(245, 245, 245),
         post=(190, 190, 190), bg=(140, 200, 230), shoulder=(232, 232, 232),
         night=False),
    dict(name="Anochecer", grass=(50, 60, 70), road=(40, 40, 48), line=(240, 220, 140),
         post=(170, 170, 180), bg=(130, 80, 140), shoulder=(180, 170, 160),
         night=False),
    dict(name="Noche",   grass=(12, 22, 14),  road=(22, 22, 28), line=(220, 220, 110),
         post=(120, 120, 140), bg=(6, 8, 18), shoulder=(120, 120, 120),
         night=True),
]

# ----------------------------------------------------------------- dificultad
DIFFICULTIES = {
    "Fácil": dict(
        traffic_period=(40, 70),
        traffic_speed=(2.0, 4.0),
        ai_max_speed_mult=0.85,
        ai_lookahead=260,
        ai_react=0.85,  # más bajo = más perezoso
    ),
    "Normal": dict(
        traffic_period=(25, 55),
        traffic_speed=(2.0, 5.0),
        ai_max_speed_mult=0.95,
        ai_lookahead=220,
        ai_react=1.0,
    ),
    "Difícil": dict(
        traffic_period=(16, 38),
        traffic_speed=(2.5, 5.5),
        ai_max_speed_mult=1.05,
        ai_lookahead=200,
        ai_react=1.2,
    ),
}

# ----------------------------------------------------------------- coches
CAR_TYPES = [
    dict(name="Cohete",  color=(255, 80, 80),  max_speed=12.5, accel=0.10, brake=0.18,
         desc="Velocidad punta alta."),
    dict(name="Garra",   color=(110, 220, 130), max_speed=10.5, accel=0.13, brake=0.22,
         desc="Aceleración rápida y mejor freno."),
    dict(name="Tanque",  color=(220, 180, 60), max_speed=10.5, accel=0.09, brake=0.16,
         desc="Equilibrado, rebote más corto."),
]

# ----------------------------------------------------------------- modos
MODES = ["Carrera", "Contrarreloj", "Supervivencia"]
TIME_TRIAL_SECONDS = 60       # segundos disponibles
SURVIVAL_SPEED_GROWTH = 0.005  # subida de velocidad mínima por segundo

# ----------------------------------------------------------------- power-ups
POWERUP_TYPES = ("turbo", "shield", "oil")
POWERUP_PERIOD = (220, 420)   # frames entre apariciones
TURBO_BOOST = 5.0             # +max_speed durante turbo
TURBO_DURATION = 90           # frames
OIL_DURATION = 80             # frames de penalización al rival
OIL_SPEED_FACTOR = 0.45

# ----------------------------------------------------------------- combo
COMBO_TIMEOUT = 90            # frames sin adelantar para resetear combo

# ----------------------------------------------------------------- audio
AUDIO_ENABLED = True
SAMPLE_RATE = 22050
