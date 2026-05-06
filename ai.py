"""IA del coche enemigo."""
import random

from config import LANES


class AIDriver:
    def __init__(self, difficulty: dict):
        self.difficulty = difficulty
        self.lane_cooldown = 0.0
        self.shield_use_cooldown = 0.0
        self.want_powerup_cooldown = 0.0

    def decide(self, car, traffic, powerups, opponent, dt) -> tuple:
        """Devuelve (left, right, up, down). Aplica rubber-banding suave."""
        self.lane_cooldown -= dt

        d = self.difficulty
        max_speed_mult = d["ai_max_speed_mult"]
        lookahead = d["ai_lookahead"]
        react = d["ai_react"]

        # Rubber-banding: si la IA va por delante mucho, ralentiza un poco;
        # si va por detrás, acelera un poco.
        gap = car.distance - opponent.distance
        if gap > 200:
            max_speed_mult *= 0.92
        elif gap < -200:
            max_speed_mult *= 1.06

        target_speed = car.base_max_speed * max_speed_mult

        # Distancia al obstáculo más cercano por delante en cada carril
        def gap_in_lane(lane):
            best = float("inf")
            for t in traffic:
                if t.lane != lane:
                    continue
                dy = car.y - t.y  # >0 cuando está por delante (en pantalla, arriba)
                if dy > 0 and dy < best:
                    best = dy
            return best

        cur_gap = gap_in_lane(car.lane)

        # Buscar power-ups apetecibles cerca y en lanes vecinos
        powerup_target_lane = None
        if powerups:
            best = None
            for p in powerups:
                if not p.alive:
                    continue
                if abs(p.lane - car.lane) <= 1:
                    dy = car.y - p.y
                    if 40 < dy < 320:
                        if best is None or dy < best[0]:
                            best = (dy, p.lane)
            if best:
                powerup_target_lane = best[1]

        up = down = left = right = False

        # Decisión de cambio de carril (solo si estamos alineados)
        if car.target_lane == car.lane and self.lane_cooldown <= 0:
            candidates = [(car.lane, cur_gap)]
            if car.lane > 0:
                candidates.append((car.lane - 1, gap_in_lane(car.lane - 1)))
            if car.lane < LANES - 1:
                candidates.append((car.lane + 1, gap_in_lane(car.lane + 1)))
            candidates.sort(key=lambda x: -x[1])
            best_lane, best_gap = candidates[0]

            # Si hay power-up cerca y nuestro hueco actual no está mal, ve a por él
            if powerup_target_lane is not None and cur_gap > 150:
                if powerup_target_lane != car.lane:
                    if powerup_target_lane < car.lane:
                        left = True
                    else:
                        right = True
                    self.lane_cooldown = 18.0 / react
            elif cur_gap < lookahead and best_lane != car.lane and best_gap > cur_gap + 70:
                if best_lane < car.lane:
                    left = True
                else:
                    right = True
                self.lane_cooldown = 18.0 / react

        # Acelerar/frenar
        if car.speed < target_speed:
            up = True
        if cur_gap < 110 and car.target_lane == car.lane:
            up = False
            down = True

        # Pequeño "error humano" para que no sea perfecta
        if random.random() < 0.005 / react:
            up, down = down, up

        return (left, right, up, down)
