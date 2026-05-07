"""Bucle principal y máquina de estados del juego."""
import math
import random
import sys

import pygame

import audio
import highscore
import ui
from ai import AIDriver
from config import (
    W, H, FPS, LANES, FINISH_DISTANCE, MAX_LIVES, CAR_W, CAR_H,
    PLAYER_BASE_Y, INVULN_AFTER_HIT,
    DIFFICULTIES, CAR_TYPES, MODES, TIME_TRIAL_SECONDS, SURVIVAL_SPEED_GROWTH,
    POWERUP_PERIOD, COMBO_TIMEOUT,
    TEXT, SUBTEXT, RED, BLUE, YELLOW, lane_center,
)
from entities import (
    Car, TrafficCar, ParticleSystem, PowerUp,
    random_traffic, random_powerup,
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Carreras 4 carriles")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "small": pygame.font.SysFont("arial", 13),
            "normal": pygame.font.SysFont("arial", 16, bold=True),
            "big": pygame.font.SysFont("arial", 32, bold=True),
            "huge": pygame.font.SysFont("arial", 96, bold=True),
        }
        audio.init()

        # Selecciones
        self.mode = "Carrera"
        self.difficulty_name = "Normal"
        self.car_index = 0
        self.menu_selected = 0

        # Estado
        self.state = "menu"  # menu | car | difficulty | mode | countdown | playing | paused | finished
        self.records = highscore.load()
        self._reset_run_state()

    # --------------------------------------------- inicializar partida
    def _reset_run_state(self):
        car_type = CAR_TYPES[self.car_index]
        self.p1 = Car("P1", lane=1, car_type=car_type, ai=False)
        # CPU usa otro coche para dar variedad
        cpu_car_type = CAR_TYPES[(self.car_index + 1) % len(CAR_TYPES)]
        self.p2 = Car("CPU", lane=2, car_type=cpu_car_type, ai=True,
                      color=BLUE)
        self.ai = AIDriver(DIFFICULTIES[self.difficulty_name])
        self.traffic: list[TrafficCar] = []
        self.powerups: list[PowerUp] = []
        self.particles = ParticleSystem()
        self.spawn_timer = 0.0
        self.powerup_timer = random.uniform(*POWERUP_PERIOD)
        self.road_offset = 0.0
        self.run_time = 0.0
        self.time_limit = TIME_TRIAL_SECONDS if self.mode == "Contrarreloj" else 0.0
        self.shake_timer = 0.0
        self.flash_timer = 0.0
        self.countdown = 3.0
        self.countdown_beat = 4
        self.winner = None
        self.last_run_summary = ""
        self.improved = False
        # Para combos: id de tráficos ya superados por cada coche
        self.p1.passed_traffic_ids = set()
        self.p2.passed_traffic_ids = set()
        # En supervivencia: velocidad mínima creciente
        self.survival_min_speed = 0.0

    # --------------------------------------------- spawn
    def spawn_traffic(self):
        diff = DIFFICULTIES[self.difficulty_name]
        car = random_traffic(diff["traffic_speed"])
        too_close = any(t.lane == car.lane and t.y < 100 for t in self.traffic)
        if not too_close:
            self.traffic.append(car)

    def spawn_powerup(self):
        p = random_powerup()
        # evita aparecer encima de un coche
        if any(abs(t.x - p.x) < CAR_W and abs(t.y - p.y) < CAR_H for t in self.traffic):
            return
        self.powerups.append(p)

    # --------------------------------------------- input humano
    def _human_inputs(self, keys):
        return (
            bool(keys[pygame.K_LEFT]),
            bool(keys[pygame.K_RIGHT]),
            bool(keys[pygame.K_UP]),
            bool(keys[pygame.K_DOWN]),
        )

    # --------------------------------------------- colisiones / lógica
    def _rects_overlap(self, ax, ay, bx, by, w=CAR_W, h=CAR_H):
        return abs(ax - bx) < w and abs(ay - by) < h

    def _check_collisions(self):
        # tráfico vs jugadores
        for p in (self.p1, self.p2):
            if p.finished or not p.alive:
                continue
            for t in self.traffic:
                if self._rects_overlap(p.x, p.y, t.x, t.y):
                    hit = p.take_hit(t, particles=self.particles)
                    if hit:
                        # apartar al de tráfico, pequeño shake y sonido
                        t.y = p.y + CAR_H + 6
                        if p is self.p1:
                            self.shake_timer = 14
                            self.flash_timer = 8
                            audio.play("crash")
                    else:
                        # rebotó por escudo
                        t.y = p.y - CAR_H - 4
                        audio.play("shield")
                    break

        # power-ups vs jugadores
        for p in (self.p1, self.p2):
            if p.finished or not p.alive:
                continue
            for pu in self.powerups:
                if not pu.alive:
                    continue
                if self._rects_overlap(p.x, p.y, pu.x, pu.y, w=40, h=40):
                    pu.alive = False
                    opp = self.p2 if p is self.p1 else self.p1
                    p.collect_powerup(pu.ptype, opponent=opp, particles=self.particles)
                    if p is self.p1:
                        audio.play("powerup" if pu.ptype != "turbo" else "turbo")
                    break
        self.powerups = [p for p in self.powerups if p.alive]

    def _update_overtakes(self):
        """Marca tráfico superado y aumenta combos cuando pasas a alguien sin chocar."""
        for p in (self.p1, self.p2):
            for t in self.traffic:
                if t.id in p.passed_traffic_ids:
                    continue
                # cuando el coche del tráfico cae por debajo del jugador en pantalla
                if t.y > p.y + CAR_H * 0.5 and p.invuln_timer <= 0 and p.alive:
                    p.passed_traffic_ids.add(t.id)
                    p.add_overtake_combo()
                    if p is self.p1 and p.combo >= 3 and p.combo % 2 == 1:
                        audio.play("combo")

    # --------------------------------------------- update por frame
    def update(self, dt):
        if self.state == "countdown":
            self.countdown -= dt / FPS
            cur_beat = max(0, int(math.ceil(self.countdown)))
            if cur_beat != self.countdown_beat and cur_beat >= 0:
                self.countdown_beat = cur_beat
                if cur_beat == 0:
                    audio.play("go")
                else:
                    audio.play("countdown")
            if self.countdown <= -0.6:
                self.state = "playing"
            return

        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        h_in = self._human_inputs(keys)
        ai_in = self.ai.decide(self.p2, self.traffic, self.powerups, self.p1, dt)

        # Activación de turbo manual del jugador (espacio): solo lo aplica si tiene turbo "guardado"
        # Para simplicidad: el espacio NO da turbo si no se cogió. La barra de turbo dura en el campo turbo_timer.

        # Mover jugadores
        self.p1.update(dt, h_in)
        self.p2.update(dt, ai_in)

        # Reloj
        self.run_time += dt / FPS
        if self.mode == "Contrarreloj":
            self.time_limit -= dt / FPS

        # En supervivencia, sube la velocidad mínima exigida
        if self.mode == "Supervivencia":
            self.survival_min_speed += SURVIVAL_SPEED_GROWTH * (dt / FPS)
            if self.p1.alive and self.p1.speed < self.survival_min_speed and self.p1.invuln_timer <= 0:
                # va demasiado lento: pierde una vida y se reactiva invulnerabilidad
                self.p1.lives = max(0, self.p1.lives - 1)
                self.p1.invuln_timer = INVULN_AFTER_HIT
                self.particles.emit_smoke(self.p1.x, self.p1.y, n=8)
                if self.p1.lives <= 0:
                    self.p1.alive = False

        # Scroll
        ref_speed = max(0.0, max(self.p1.speed, self.p2.speed))
        self.road_offset += ref_speed * dt
        if ref_speed > 7:
            self.particles.emit_speedlines(self.p1.x, self.p1.y, n=1)

        # humo del tubo
        if self.p1.alive and self.p1.speed > 0.5 and random.random() < 0.4:
            self.particles.emit_smoke(self.p1.x, self.p1.y + CAR_H // 2 + 4, n=1,
                                      color=(160, 160, 160))
        if self.p2.alive and self.p2.speed > 0.5 and random.random() < 0.4:
            self.particles.emit_smoke(self.p2.x, self.p2.y + CAR_H // 2 + 4, n=1,
                                      color=(160, 160, 160))

        # Mover tráfico
        for t in self.traffic:
            t.y += (ref_speed - t.speed) * dt
        self.traffic = [t for t in self.traffic if t.y < H + 100]

        # Mover power-ups
        for p in self.powerups:
            p.y += ref_speed * dt
        self.powerups = [p for p in self.powerups if p.y < H + 50]

        # Spawning
        diff = DIFFICULTIES[self.difficulty_name]
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_traffic()
            lo, hi = diff["traffic_period"]
            self.spawn_timer = random.uniform(lo, hi)

        self.powerup_timer -= dt
        if self.powerup_timer <= 0:
            self.spawn_powerup()
            self.powerup_timer = random.uniform(*POWERUP_PERIOD)

        # Colisiones / adelantamientos
        self._check_collisions()
        self._update_overtakes()

        # Partículas
        self.particles.update(dt)

        # Shake / flash
        if self.shake_timer > 0:
            self.shake_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Fin de partida según modo
        self._check_finish()

    def _check_finish(self):
        if self.winner is not None:
            return
        if self.mode == "Carrera":
            # Solo se gana cruzando la meta. Un coche eliminado deja de correr,
            # pero el otro tiene que llegar a la meta para ganar.
            if self.p1.alive and self.p1.distance >= FINISH_DISTANCE and not self.p1.finished:
                self.p1.finished = True
            if self.p2.alive and self.p2.distance >= FINISH_DISTANCE and not self.p2.finished:
                self.p2.finished = True

            if self.p1.finished and self.p2.finished:
                # cruzaron en el mismo frame: gana el que esté más adelantado
                self._end(winner=self.p1 if self.p1.distance >= self.p2.distance else self.p2)
            elif self.p1.finished:
                self._end(winner=self.p1)
            elif self.p2.finished:
                self._end(winner=self.p2)
            elif not self.p1.alive and not self.p2.alive:
                # nadie puede llegar ya
                self._end(winner=None, reason="Nadie llegó a la meta")
        elif self.mode == "Contrarreloj":
            if self.time_limit <= 0 or not self.p1.alive:
                w = self.p1 if self.p1.distance >= self.p2.distance else self.p2
                self._end(winner=w, reason="Fin del tiempo")
        elif self.mode == "Supervivencia":
            if not self.p1.alive:
                self._end(winner=None, reason="Aguantaste " + f"{self.run_time:.1f}s")

    def _end(self, winner, reason=""):
        self.winner = winner
        self.state = "finished"
        if winner is self.p1:
            audio.play("finish")
        else:
            audio.play("crash")
        # records
        time_arg = self.run_time if self.mode in ("Carrera", "Supervivencia") else None
        improved = highscore.update_for_run(
            self.records, self.mode, self.p1.distance, time_arg
        )
        self.improved = improved
        highscore.save(self.records)

    # --------------------------------------------- render
    def render(self):
        # offset de shake
        ox = oy = 0
        if self.shake_timer > 0:
            ox = random.randint(-6, 6)
            oy = random.randint(-6, 6)

        target = self.screen
        if ox or oy:
            target = pygame.Surface((W, H))
        ui.draw_road(target, self.road_offset, max(self.p1.distance, 0))

        # tráfico
        for t in self.traffic:
            ui.draw_traffic_car(target, t)

        # power-ups
        for p in self.powerups:
            ui.draw_powerup(target, p)

        # partículas (debajo de los coches)
        ui.draw_particles(target, self.particles)

        # coches
        if self.p1.alive:
            blink = self.p1.invuln_timer > 0 and not self.p1.shield
            ui.draw_car(target, self.p1, blink=blink)
        if self.p2.alive:
            blink = self.p2.invuln_timer > 0 and not self.p2.shield
            ui.draw_car(target, self.p2, blink=blink)

        # flash blanco
        if self.flash_timer > 0:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            alpha = int(180 * (self.flash_timer / 8))
            s.fill((255, 255, 255, alpha))
            target.blit(s, (0, 0))

        if target is not self.screen:
            self.screen.fill((0, 0, 0))
            self.screen.blit(target, (ox, oy))

        # HUD (sobre la pantalla, no afectado por shake)
        ui.draw_progress(self.screen, self.p1.distance, self.p2.distance)
        ui.draw_minimap(self.screen, self.p1, self.p2)
        time_disp = (self.time_limit if self.mode == "Contrarreloj"
                     else self.run_time if self.mode == "Supervivencia" else 0.0)
        ui.draw_hud(
            self.screen, self.fonts, self.p1, self.p2, self.mode,
            time_disp, self.p1.distance, self.p1.combo,
            paused=(self.state == "paused"),
        )

        # estados especiales
        if self.state == "menu":
            self._render_menu()
        elif self.state == "mode":
            ui.draw_menu(self.screen, self.fonts, "Selecciona modo",
                         MODES, self.menu_selected,
                         "↑↓ moverse · Enter aceptar · Esc volver")
        elif self.state == "difficulty":
            ui.draw_menu(self.screen, self.fonts, "Dificultad",
                         list(DIFFICULTIES.keys()), self.menu_selected,
                         "↑↓ moverse · Enter aceptar · Esc volver")
        elif self.state == "car":
            self._render_car_select()
        elif self.state == "countdown":
            ui.draw_countdown(self.screen, self.fonts, max(0.0, self.countdown))
        elif self.state == "finished":
            self._render_finished()

        pygame.display.flip()

    def _render_menu(self):
        rec = self.records.get(self.mode, {})
        bd = int(rec.get("best_distance", 0))
        bt = rec.get("best_time")
        bt_str = (f"  ·  mejor tiempo: {bt:.1f}s" if bt else "")
        footer = f"Modo: {self.mode}  ·  Dificultad: {self.difficulty_name}  ·  Coche: {CAR_TYPES[self.car_index]['name']}\nMejor: {bd} m{bt_str}"
        ui.draw_menu(
            self.screen, self.fonts, "Carreras 4 Carriles",
            ["Empezar", "Modo", "Dificultad", "Coche", "Salir"],
            self.menu_selected, footer,
        )

    def _render_car_select(self):
        car = CAR_TYPES[self.car_index]
        ui.draw_menu(
            self.screen, self.fonts, "Selecciona coche",
            [c["name"] for c in CAR_TYPES],
            self.menu_selected,
            f"{car['desc']}   max {car['max_speed']:.1f}  acel {car['accel']:.2f}",
        )
        # vista previa del coche elegido
        preview = type("preview", (), {})()
        preview.x = W // 2
        preview.y = H - 240
        preview.color = car["color"]
        preview.shield = False
        preview.turbo_timer = 0
        preview.bounce_timer = 0
        ui.draw_car(self.screen, preview)

    def _render_finished(self):
        if self.winner is self.p1:
            title = "¡Ganaste!"
        elif self.winner is self.p2:
            title = "Gana la CPU"
        else:
            title = "Fin de partida"
        msg = f"P1 {int(self.p1.distance)} m   ·   CPU {int(self.p2.distance)} m   ·   {self.run_time:.1f}s"
        if self.improved:
            msg += "   ¡Récord nuevo!"
        ui.draw_overlay(self.screen, self.fonts, title, msg,
                        "Enter o R para volver al menú · Esc para salir")

    # --------------------------------------------- eventos
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._quit()
        if event.type != pygame.KEYDOWN:
            return
        k = event.key

        if k == pygame.K_ESCAPE:
            if self.state in ("menu",):
                self._quit()
            elif self.state in ("mode", "difficulty", "car"):
                self.state = "menu"
                self.menu_selected = 0
            else:
                # sale al menú principal
                self.state = "menu"
                self.menu_selected = 0
            return

        if self.state == "menu":
            self._menu_keys(k)
        elif self.state == "mode":
            opts = MODES
            self._list_keys(k, opts, on_accept=self._accept_mode)
        elif self.state == "difficulty":
            opts = list(DIFFICULTIES.keys())
            self._list_keys(k, opts, on_accept=self._accept_difficulty)
        elif self.state == "car":
            opts = [c["name"] for c in CAR_TYPES]
            self._list_keys(k, opts, on_accept=self._accept_car)
        elif self.state in ("playing", "paused"):
            if k == pygame.K_p:
                self.state = "paused" if self.state == "playing" else "playing"
            elif k == pygame.K_r:
                self._start_run()
        elif self.state == "finished":
            if k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r, pygame.K_SPACE):
                self.state = "menu"
                self.menu_selected = 0

    def _quit(self):
        audio.stop_all()
        pygame.quit()
        sys.exit(0)

    def _menu_keys(self, k):
        opts = ["Empezar", "Modo", "Dificultad", "Coche", "Salir"]
        if k in (pygame.K_UP, pygame.K_w):
            self.menu_selected = (self.menu_selected - 1) % len(opts)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.menu_selected = (self.menu_selected + 1) % len(opts)
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            sel = opts[self.menu_selected]
            if sel == "Empezar":
                self._start_run()
            elif sel == "Modo":
                self.menu_selected = MODES.index(self.mode)
                self.state = "mode"
            elif sel == "Dificultad":
                self.menu_selected = list(DIFFICULTIES.keys()).index(self.difficulty_name)
                self.state = "difficulty"
            elif sel == "Coche":
                self.menu_selected = self.car_index
                self.state = "car"
            elif sel == "Salir":
                self._quit()

    def _list_keys(self, k, opts, on_accept):
        if k in (pygame.K_UP, pygame.K_w):
            self.menu_selected = (self.menu_selected - 1) % len(opts)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.menu_selected = (self.menu_selected + 1) % len(opts)
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            on_accept(self.menu_selected)
            self.state = "menu"
            self.menu_selected = 0

    def _accept_mode(self, idx):
        self.mode = MODES[idx]

    def _accept_difficulty(self, idx):
        self.difficulty_name = list(DIFFICULTIES.keys())[idx]

    def _accept_car(self, idx):
        self.car_index = idx

    def _start_run(self):
        self._reset_run_state()
        self.state = "countdown"
        self.countdown = 3.0
        self.countdown_beat = 4
        audio.play("countdown")

    # --------------------------------------------- bucle
    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = min(2.0, (dt_ms / 1000.0) * FPS)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.render()
