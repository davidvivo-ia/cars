"""Carrera de dos coches en una carretera de 4 carriles.

Controles:
  Jugador 1 (rojo): flechas (Izq/Der carril, Arriba acelerar, Abajo frenar)
  Jugador 2 (azul): A/D carril, W acelerar, S frenar
  R: reiniciar    Esc: salir

Gana el primero en llegar a 3000 m.
"""

import math
import random
import sys

import pygame

# ---------------------------------------------------------------- constantes
W, H = 600, 700
FPS = 60

LANES = 4
ROAD_LEFT = 60
ROAD_RIGHT = W - 60
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH / LANES

CAR_W, CAR_H = 38, 64
FINISH_DISTANCE = 3000  # metros

# Colores
GRASS = (31, 94, 42)
ROAD = (42, 42, 42)
LINE = (245, 245, 245)
SHOULDER = (232, 232, 232)
POST = (187, 187, 187)
BG = (17, 17, 17)
TEXT = (235, 235, 235)
SUBTEXT = (160, 160, 160)
RED = (255, 80, 80)
BLUE = (80, 168, 255)
TRAFFIC_COLORS = [
    (224, 192, 64),
    (154, 74, 214),
    (63, 191, 111),
    (217, 107, 31),
    (204, 204, 204),
]


def lane_center(i: int) -> float:
    return ROAD_LEFT + LANE_WIDTH * (i + 0.5)


# ---------------------------------------------------------------- entidades
class Car:
    def __init__(self, color, lane, controls, name):
        self.color = color
        self.name = name
        self.lane = lane
        self.target_lane = lane
        self.x = lane_center(lane)
        self.y = H - 120
        self.speed = 0.0          # px por "frame de referencia"
        self.max_speed = 11.0
        self.accel = 0.08
        self.brake = 0.18
        self.drag = 0.02
        self.distance = 0.0       # metros
        self.controls = controls  # dict: left, right, up, down -> pygame keys
        self.crashed = False
        self.crash_timer = 0.0
        self.finished = False

    def update(self, dt, keys):
        if self.finished:
            return

        if self.crashed:
            self.crash_timer -= dt
            self.speed *= 0.92
            if self.crash_timer <= 0:
                self.crashed = False
                self.speed = 2.0
        else:
            # cambio de carril (un paso por pulsación sostenida hasta llegar)
            if keys[self.controls["left"]] and self.target_lane == self.lane and self.lane > 0:
                self.target_lane = self.lane - 1
            if keys[self.controls["right"]] and self.target_lane == self.lane and self.lane < LANES - 1:
                self.target_lane = self.lane + 1

            tx = lane_center(self.target_lane)
            dx = tx - self.x
            move = math.copysign(min(abs(dx), 6.0 * dt), dx) if dx != 0 else 0
            self.x += move
            if abs(self.x - tx) < 1:
                self.x = tx
                self.lane = self.target_lane

            if keys[self.controls["up"]]:
                self.speed += self.accel * dt
            elif keys[self.controls["down"]]:
                self.speed -= self.brake * dt
            else:
                self.speed -= self.drag * dt
            self.speed = max(0.0, min(self.max_speed, self.speed))

        self.distance += self.speed * dt * 0.5
        if self.distance >= FINISH_DISTANCE:
            self.distance = FINISH_DISTANCE
            self.finished = True


class TrafficCar:
    def __init__(self):
        self.lane = random.randint(0, LANES - 1)
        self.x = lane_center(self.lane)
        self.y = -CAR_H - 20
        self.speed = 2.0 + random.random() * 3.0
        self.color = random.choice(TRAFFIC_COLORS)


# ------------------------------------------------------------------- juego
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Carrera de Dos Coches - 4 Carriles")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 16, bold=True)
        self.font_big = pygame.font.SysFont("arial", 36, bold=True)
        self.font_small = pygame.font.SysFont("arial", 13)
        self.reset()
        self.state = "menu"  # menu | playing | finished
        self.winner = None

    def reset(self):
        self.p1 = Car(RED, 1, {
            "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
            "up": pygame.K_UP, "down": pygame.K_DOWN,
        }, "Jugador 1")
        self.p2 = Car(BLUE, 2, {
            "left": pygame.K_a, "right": pygame.K_d,
            "up": pygame.K_w, "down": pygame.K_s,
        }, "Jugador 2")
        self.traffic = []
        self.spawn_timer = 0.0
        self.road_offset = 0.0
        self.winner = None

    # ------------------------------------------------------- lógica
    def spawn_traffic(self):
        car = TrafficCar()
        too_close = any(t.lane == car.lane and t.y < 80 for t in self.traffic)
        if not too_close:
            self.traffic.append(car)

    def rects_overlap(self, ax, ay, bx, by):
        return abs(ax - bx) < CAR_W and abs(ay - by) < CAR_H

    def check_collisions(self):
        for p in (self.p1, self.p2):
            if p.crashed or p.finished:
                continue
            for t in self.traffic:
                if self.rects_overlap(p.x, p.y, t.x, t.y):
                    p.crashed = True
                    p.crash_timer = 60.0
                    p.speed = 0
                    break

        if not (self.p1.crashed or self.p2.crashed or self.p1.finished or self.p2.finished):
            if self.rects_overlap(self.p1.x, self.p1.y, self.p2.x, self.p2.y):
                self.p1.crashed = self.p2.crashed = True
                self.p1.crash_timer = self.p2.crash_timer = 50.0
                self.p1.speed = self.p2.speed = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.p1.update(dt, keys)
        self.p2.update(dt, keys)

        ref_speed = max(self.p1.speed, self.p2.speed)
        self.road_offset = (self.road_offset + ref_speed * dt) % 44

        for t in self.traffic:
            t.y += (ref_speed - t.speed) * dt
        self.traffic = [t for t in self.traffic if t.y < H + 100]

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_traffic()
            self.spawn_timer = 25 + random.random() * 30

        self.check_collisions()

        if not self.winner:
            if self.p1.finished and self.p2.finished:
                self.winner = self.p1 if self.p1.distance >= self.p2.distance else self.p2
                self.state = "finished"
            elif self.p1.finished:
                self.winner = self.p1
                self.state = "finished"
            elif self.p2.finished:
                self.winner = self.p2
                self.state = "finished"

    # ------------------------------------------------------- dibujo
    def draw_road(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, GRASS, (0, 0, ROAD_LEFT, H))
        pygame.draw.rect(self.screen, GRASS, (ROAD_RIGHT, 0, W - ROAD_RIGHT, H))
        pygame.draw.rect(self.screen, ROAD, (ROAD_LEFT, 0, ROAD_WIDTH, H))
        pygame.draw.rect(self.screen, SHOULDER, (ROAD_LEFT - 4, 0, 4, H))
        pygame.draw.rect(self.screen, SHOULDER, (ROAD_RIGHT, 0, 4, H))

        # líneas discontinuas que parecen avanzar
        dash_len, gap_len = 24, 20
        period = dash_len + gap_len
        for i in range(1, LANES):
            x = int(ROAD_LEFT + LANE_WIDTH * i)
            y = -period + (self.road_offset % period)
            while y < H:
                pygame.draw.rect(self.screen, LINE, (x - 1, int(y), 3, dash_len))
                y += period

        # postes laterales con parallax
        post_spacing = 80
        offset = (self.road_offset * 2) % post_spacing
        y = offset - post_spacing
        while y < H:
            pygame.draw.rect(self.screen, POST, (ROAD_LEFT - 14, int(y), 6, 14))
            pygame.draw.rect(self.screen, POST, (ROAD_RIGHT + 8, int(y), 6, 14))
            y += post_spacing

    def draw_car(self, x, y, color, crashed=False):
        x, y = int(x), int(y)
        # sombra
        shadow = pygame.Rect(x - CAR_W // 2 + 3, y - CAR_H // 2 + 5, CAR_W, CAR_H)
        s = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 90))
        self.screen.blit(s, shadow.topleft)

        # carrocería
        body = pygame.Rect(x - CAR_W // 2, y - CAR_H // 2, CAR_W, CAR_H)
        pygame.draw.rect(self.screen, color, body, border_radius=6)

        # parabrisas
        ws1 = pygame.Rect(x - CAR_W // 2 + 5, y - CAR_H // 2 + 8, CAR_W - 10, 18)
        ws2 = pygame.Rect(x - CAR_W // 2 + 5, y + CAR_H // 2 - 22, CAR_W - 10, 14)
        pygame.draw.rect(self.screen, (20, 30, 50), ws1, border_radius=3)
        pygame.draw.rect(self.screen, (20, 30, 50), ws2, border_radius=3)

        # ruedas
        wheel_color = (17, 17, 17)
        pygame.draw.rect(self.screen, wheel_color, (x - CAR_W // 2 - 3, y - CAR_H // 2 + 6, 5, 14))
        pygame.draw.rect(self.screen, wheel_color, (x + CAR_W // 2 - 2, y - CAR_H // 2 + 6, 5, 14))
        pygame.draw.rect(self.screen, wheel_color, (x - CAR_W // 2 - 3, y + CAR_H // 2 - 20, 5, 14))
        pygame.draw.rect(self.screen, wheel_color, (x + CAR_W // 2 - 2, y + CAR_H // 2 - 20, 5, 14))

        # faros
        pygame.draw.rect(self.screen, (255, 247, 176), (x - CAR_W // 2 + 4, y - CAR_H // 2 + 1, 8, 4))
        pygame.draw.rect(self.screen, (255, 247, 176), (x + CAR_W // 2 - 12, y - CAR_H // 2 + 1, 8, 4))

        if crashed:
            r = 8 + int(math.sin(pygame.time.get_ticks() / 60) * 2)
            pygame.draw.circle(self.screen, (200, 80, 40), (x, y - CAR_H // 2 - 6), r)

    def draw_progress(self):
        bar_x, bar_y, bar_w, bar_h = ROAD_LEFT, 12, ROAD_WIDTH, 8
        bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 40))
        self.screen.blit(bg, (bar_x, bar_y))
        f1 = self.p1.distance / FINISH_DISTANCE
        f2 = self.p2.distance / FINISH_DISTANCE
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, int(bar_w * f1), bar_h // 2))
        pygame.draw.rect(self.screen, BLUE, (bar_x, bar_y + bar_h // 2, int(bar_w * f2), bar_h // 2))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x + bar_w - 2, bar_y - 4, 2, bar_h + 8))

    def draw_hud(self):
        p1_text = f"P1 (Rojo)  {int(self.p1.distance)} m   {int(self.p1.speed * 22)} km/h"
        p2_text = f"P2 (Azul)  {int(self.p2.distance)} m   {int(self.p2.speed * 22)} km/h"
        self.screen.blit(self.font.render(p1_text, True, RED), (12, H - 50))
        self.screen.blit(self.font.render(p2_text, True, BLUE), (12, H - 28))
        help_text = "P1: Flechas   P2: WASD   R: reiniciar   Esc: salir"
        surf = self.font_small.render(help_text, True, SUBTEXT)
        self.screen.blit(surf, (W - surf.get_width() - 12, H - 22))

    def draw_overlay(self, title, msg, hint):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        t = self.font_big.render(title, True, TEXT)
        self.screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 70))
        m = self.font.render(msg, True, TEXT)
        self.screen.blit(m, (W // 2 - m.get_width() // 2, H // 2 - 20))
        h = self.font_small.render(hint, True, SUBTEXT)
        self.screen.blit(h, (W // 2 - h.get_width() // 2, H // 2 + 20))

    def render(self):
        self.draw_road()
        for t in self.traffic:
            self.draw_car(t.x, t.y, t.color)
        self.draw_car(self.p1.x, self.p1.y, self.p1.color, self.p1.crashed)
        self.draw_car(self.p2.x, self.p2.y, self.p2.color, self.p2.crashed)
        self.draw_progress()
        self.draw_hud()

        if self.state == "menu":
            self.draw_overlay(
                "Carrera de Dos Coches",
                "4 carriles, mucho tráfico, un ganador.",
                "Pulsa ESPACIO para empezar",
            )
        elif self.state == "finished" and self.winner:
            name = "Jugador 1 (Rojo)" if self.winner is self.p1 else "Jugador 2 (Azul)"
            self.draw_overlay(
                f"¡{name} gana!",
                f"P1: {int(self.p1.distance)} m    P2: {int(self.p2.distance)} m",
                "Pulsa R para jugar de nuevo, Esc para salir",
            )

        pygame.display.flip()

    # ------------------------------------------------------- bucle
    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = (dt_ms / 1000.0) * FPS  # frames de referencia por tick
            dt = min(dt, 2.0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_r:
                        self.reset()
                        self.state = "playing"
                    if event.key == pygame.K_SPACE and self.state == "menu":
                        self.state = "playing"

            if self.state == "playing":
                self.update(dt)

            self.render()


if __name__ == "__main__":
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
