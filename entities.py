"""Coches, tráfico, power-ups y partículas."""
import math
import random

from config import (
    CAR_W, CAR_H, LANES, lane_center, PLAYER_BASE_Y, INVULN_AFTER_HIT,
    FINISH_DISTANCE, MAX_LIVES, TRAFFIC_COLORS, POWERUP_TYPES,
    TURBO_BOOST, TURBO_DURATION, OIL_DURATION, OIL_SPEED_FACTOR,
)


# --------------------------------------------------------------- partículas
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "kind")

    def __init__(self, x, y, vx, vy, life, color, size=4, kind="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.kind = kind

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return max(0, min(255, int(255 * (self.life / self.max_life))))


class ParticleSystem:
    def __init__(self):
        self.items: list[Particle] = []

    def update(self, dt):
        self.items = [p for p in self.items if p.alive]
        for p in self.items:
            p.update(dt)

    def emit_smoke(self, x, y, n=1, color=(180, 180, 180)):
        for _ in range(n):
            ang = random.uniform(-math.pi, 0)
            speed = random.uniform(0.5, 1.8)
            self.items.append(Particle(
                x + random.uniform(-3, 3),
                y + random.uniform(-2, 2),
                math.cos(ang) * speed * 0.3,
                math.sin(ang) * speed,
                life=random.uniform(20, 35),
                color=color,
                size=random.randint(3, 6),
            ))

    def emit_sparks(self, x, y, n=14, color=(255, 200, 80)):
        for _ in range(n):
            ang = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.items.append(Particle(
                x, y,
                math.cos(ang) * speed,
                math.sin(ang) * speed,
                life=random.uniform(10, 20),
                color=color,
                size=random.randint(2, 4),
            ))

    def emit_dust(self, x, y, n=6, color=(160, 140, 90)):
        for _ in range(n):
            self.items.append(Particle(
                x + random.uniform(-CAR_W / 2, CAR_W / 2),
                y + random.uniform(-2, 2),
                random.uniform(-1, 1),
                random.uniform(0.5, 2.0),
                life=random.uniform(15, 25),
                color=color,
                size=random.randint(2, 4),
            ))

    def emit_speedlines(self, x, y, n=2, color=(255, 255, 255)):
        for _ in range(n):
            self.items.append(Particle(
                x + random.uniform(-CAR_W, CAR_W),
                y + random.uniform(-CAR_H, CAR_H),
                0,
                random.uniform(8, 14),
                life=random.uniform(6, 12),
                color=color,
                size=2,
                kind="line",
            ))


# --------------------------------------------------------------- coches
class Car:
    """Coche del jugador o de la IA."""

    def __init__(self, name, lane, car_type, controls=None, ai=False, color=None):
        self.name = name
        self.car_type = car_type
        self.color = color if color is not None else car_type["color"]
        self.lane = lane
        self.target_lane = lane
        self.x = lane_center(lane)
        self.y = PLAYER_BASE_Y
        self.base_y = self.y
        self.speed = 0.0
        self.base_max_speed = float(car_type["max_speed"])
        self.max_speed = self.base_max_speed
        self.min_speed = -4.0
        self.accel = float(car_type["accel"])
        self.brake = float(car_type["brake"])
        self.drag = 0.02
        self.distance = 0.0
        self.controls = controls
        self.ai = ai
        # Estados
        self.bounce_timer = 0.0
        self.invuln_timer = 0.0
        self.lives = MAX_LIVES
        self.shield = False
        self.turbo_timer = 0.0
        self.oil_timer = 0.0
        self.finished = False
        self.alive = True
        # combo
        self.combo = 0
        self.combo_timer = 0.0
        # adelantamientos contables (id de tráfico ya superado)
        self.passed_traffic_ids: set = set()

    # -------------------------------------------- estado
    @property
    def display_speed_kmh(self) -> int:
        return int(max(0.0, self.speed) * 22)

    def take_hit(self, traffic_car=None, particles: ParticleSystem | None = None):
        if self.invuln_timer > 0 or self.finished or not self.alive:
            return False
        if self.shield:
            self.shield = False
            self.invuln_timer = INVULN_AFTER_HIT * 0.6
            if particles:
                particles.emit_sparks(self.x, self.y, n=18, color=(120, 200, 255))
            return False
        # rebote
        self.speed = -3.5
        self.bounce_timer = 22.0
        self.invuln_timer = INVULN_AFTER_HIT
        self.combo = 0
        self.combo_timer = 0
        self.lives = max(0, self.lives - 1)
        if self.lives <= 0:
            self.alive = False
        if particles:
            particles.emit_sparks(self.x, self.y, n=20)
            particles.emit_smoke(self.x, self.y, n=10, color=(80, 80, 80))
        return True

    def collect_powerup(self, ptype: str, opponent: "Car | None" = None,
                        particles: ParticleSystem | None = None):
        if ptype == "turbo":
            self.turbo_timer = max(self.turbo_timer, TURBO_DURATION)
        elif ptype == "shield":
            self.shield = True
        elif ptype == "oil" and opponent is not None:
            opponent.oil_timer = max(opponent.oil_timer, OIL_DURATION)
        if particles:
            particles.emit_sparks(self.x, self.y, n=10,
                                  color=(120, 220, 255) if ptype == "shield"
                                  else (255, 220, 100) if ptype == "turbo"
                                  else (180, 130, 90))

    def add_overtake_combo(self):
        self.combo += 1
        self.combo_timer = 90.0  # frames

    # -------------------------------------------- update
    def update(self, dt, inputs):
        """inputs: tuple (left, right, up, down). Devuelve True si vivo y jugando."""
        if not self.alive or self.finished:
            self.speed = max(0.0, self.speed - 0.05 * dt)
            return False

        # timers
        if self.bounce_timer > 0:
            self.bounce_timer -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        if self.turbo_timer > 0:
            self.turbo_timer -= dt
        if self.oil_timer > 0:
            self.oil_timer -= dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        # max speed con boost / penalización
        ms = self.base_max_speed
        if self.turbo_timer > 0:
            ms += TURBO_BOOST
        if self.oil_timer > 0:
            ms *= OIL_SPEED_FACTOR
        self.max_speed = ms

        left, right, up, down = inputs

        # cambio de carril
        if left and self.target_lane == self.lane and self.lane > 0:
            self.target_lane = self.lane - 1
        if right and self.target_lane == self.lane and self.lane < LANES - 1:
            self.target_lane = self.lane + 1

        tx = lane_center(self.target_lane)
        dx = tx - self.x
        if dx != 0:
            move = math.copysign(min(abs(dx), 6.0 * dt), dx)
            self.x += move
        if abs(self.x - tx) < 1:
            self.x = tx
            self.lane = self.target_lane

        # control de velocidad
        if self.bounce_timer > 0:
            # Velocidad recupera hacia 0
            if self.speed < 0:
                self.speed += 0.18 * dt
            else:
                self.speed = max(0.0, self.speed - 0.05 * dt)
        else:
            if up:
                self.speed += self.accel * dt
            elif down:
                self.speed -= self.brake * dt
            else:
                self.speed -= self.drag * dt
        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

        if self.bounce_timer > 0:
            self.y = self.base_y + min(20, self.bounce_timer * 0.6)
        else:
            self.y = self.base_y

        self.distance += self.speed * dt * 0.5
        self.distance = max(0.0, self.distance)
        return True


# --------------------------------------------------------------- tráfico
class TrafficCar:
    _next_id = 0

    def __init__(self, lane, speed, color):
        self.id = TrafficCar._next_id
        TrafficCar._next_id += 1
        self.lane = lane
        self.x = lane_center(lane)
        self.y = -CAR_H - 20
        self.speed = speed
        self.color = color


def random_traffic(traffic_speed_range, lane: int | None = None) -> TrafficCar:
    if lane is None:
        lane = random.randint(0, LANES - 1)
    lo, hi = traffic_speed_range
    return TrafficCar(lane, random.uniform(lo, hi), random.choice(TRAFFIC_COLORS))


# --------------------------------------------------------------- power-ups
class PowerUp:
    def __init__(self, lane, ptype):
        self.lane = lane
        self.x = lane_center(lane)
        self.y = -30
        self.ptype = ptype  # "turbo" | "shield" | "oil"
        self.alive = True


def random_powerup() -> PowerUp:
    return PowerUp(random.randint(0, LANES - 1), random.choice(POWERUP_TYPES))
