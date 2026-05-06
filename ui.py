"""Funciones de dibujo: carretera con curvas, HUD, mini-mapa, overlays."""
import math

import pygame

from config import (
    W, H, ROAD_LEFT, ROAD_RIGHT, ROAD_WIDTH, LANES, LANE_WIDTH,
    CAR_W, CAR_H, FINISH_DISTANCE, MAX_LIVES,
    TEXT, SUBTEXT, RED, BLUE, YELLOW, GREEN, PURPLE, CYAN, ORANGE,
    THEMES,
)


# ----------------------------------------------------------------- temas
def theme_for_distance(distance: float) -> dict:
    """Cambia de tema cada 1000 m."""
    idx = int(distance // 1000) % len(THEMES)
    return THEMES[idx]


def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def blended_theme(distance: float) -> dict:
    """Mezcla suavemente entre temas vecinos en el último tramo de 200 m."""
    seg = 1000
    transition = 200
    pos = distance % seg
    base_idx = int(distance // seg) % len(THEMES)
    a = THEMES[base_idx]
    if pos > seg - transition:
        b = THEMES[(base_idx + 1) % len(THEMES)]
        t = (pos - (seg - transition)) / transition
        return {
            "name": a["name"],
            "grass": lerp_color(a["grass"], b["grass"], t),
            "road": lerp_color(a["road"], b["road"], t),
            "line": lerp_color(a["line"], b["line"], t),
            "post": lerp_color(a["post"], b["post"], t),
            "bg": lerp_color(a["bg"], b["bg"], t),
            "shoulder": lerp_color(a["shoulder"], b["shoulder"], t),
            "night": a["night"] or b["night"],
        }
    return a


# ----------------------------------------------------------------- carretera
def curve_offset(road_offset: float, distance: float, y: int) -> float:
    """Pequeño zigzag horizontal de la carretera para romper la verticalidad."""
    # La curva avanza con la distancia recorrida. y desplaza la fase verticalmente.
    phase = distance * 0.002 + y * 0.01
    return math.sin(phase) * 18 + math.sin(phase * 0.5) * 8


def draw_road(screen, road_offset, distance):
    theme = blended_theme(distance)
    screen.fill(theme["bg"])

    # césped lateral
    pygame.draw.rect(screen, theme["grass"], (0, 0, ROAD_LEFT, H))
    pygame.draw.rect(screen, theme["grass"], (ROAD_RIGHT, 0, W - ROAD_RIGHT, H))

    # asfalto con curvas: dibujamos por filas
    road_color = theme["road"]
    shoulder_color = theme["shoulder"]
    grass_color = theme["grass"]
    step = 8
    for y in range(0, H, step):
        off = curve_offset(road_offset, distance, y)
        x_left = ROAD_LEFT + off
        # césped que invade por desplazamiento
        pygame.draw.rect(screen, grass_color, (0, y, max(0, x_left), step))
        pygame.draw.rect(screen, grass_color, (ROAD_RIGHT + off, y, max(0, W - (ROAD_RIGHT + off)), step))
        pygame.draw.rect(screen, road_color, (x_left, y, ROAD_WIDTH, step))
        pygame.draw.rect(screen, shoulder_color, (x_left - 4, y, 4, step))
        pygame.draw.rect(screen, shoulder_color, (x_left + ROAD_WIDTH, y, 4, step))

    # líneas de carril discontinuas con efecto de avance
    dash_len, gap_len = 24, 20
    period = dash_len + gap_len
    line_color = theme["line"]
    for i in range(1, LANES):
        for y_start in range(int(-period + (road_offset % period)), H, period):
            off = curve_offset(road_offset, distance, y_start)
            x = int(ROAD_LEFT + LANE_WIDTH * i + off)
            pygame.draw.rect(screen, line_color, (x - 1, y_start, 3, dash_len))

    # postes laterales (parallax)
    post_spacing = 80
    base_off = (road_offset * 2) % post_spacing
    y = base_off - post_spacing
    while y < H:
        off = curve_offset(road_offset, distance, int(y))
        pygame.draw.rect(screen, theme["post"], (int(ROAD_LEFT + off - 14), int(y), 6, 14))
        pygame.draw.rect(screen, theme["post"], (int(ROAD_RIGHT + off + 8), int(y), 6, 14))
        y += post_spacing

    # estrellas si es de noche
    if theme["night"]:
        random_seed_dots(screen, road_offset)
    return theme


_STARS = None


def random_seed_dots(screen, road_offset):
    global _STARS
    if _STARS is None:
        import random
        rng = random.Random(42)
        _STARS = [(rng.randint(0, ROAD_LEFT - 6), rng.randint(0, H), rng.randint(0, 1)) for _ in range(40)]
        _STARS += [(rng.randint(ROAD_RIGHT + 6, W), rng.randint(0, H), rng.randint(0, 1)) for _ in range(40)]
    color = (240, 240, 200)
    for x, y, b in _STARS:
        s = 1 + b
        pygame.draw.rect(screen, color, (x, y, s, s))


# ----------------------------------------------------------------- coche
def draw_car(screen, car, blink=False):
    x, y = int(car.x), int(car.y)
    if blink and (pygame.time.get_ticks() // 80) % 2 == 0:
        return  # parpadeo durante invulnerabilidad

    # sombra
    s = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 90))
    screen.blit(s, (x - CAR_W // 2 + 3, y - CAR_H // 2 + 5))

    # carrocería
    body = pygame.Rect(x - CAR_W // 2, y - CAR_H // 2, CAR_W, CAR_H)
    pygame.draw.rect(screen, car.color, body, border_radius=6)

    # parabrisas
    pygame.draw.rect(screen, (20, 30, 50),
                     (x - CAR_W // 2 + 5, y - CAR_H // 2 + 8, CAR_W - 10, 18),
                     border_radius=3)
    pygame.draw.rect(screen, (20, 30, 50),
                     (x - CAR_W // 2 + 5, y + CAR_H // 2 - 22, CAR_W - 10, 14),
                     border_radius=3)

    # ruedas
    wheel = (17, 17, 17)
    pygame.draw.rect(screen, wheel, (x - CAR_W // 2 - 3, y - CAR_H // 2 + 6, 5, 14))
    pygame.draw.rect(screen, wheel, (x + CAR_W // 2 - 2, y - CAR_H // 2 + 6, 5, 14))
    pygame.draw.rect(screen, wheel, (x - CAR_W // 2 - 3, y + CAR_H // 2 - 20, 5, 14))
    pygame.draw.rect(screen, wheel, (x + CAR_W // 2 - 2, y + CAR_H // 2 - 20, 5, 14))

    # faros
    pygame.draw.rect(screen, (255, 247, 176), (x - CAR_W // 2 + 4, y - CAR_H // 2 + 1, 8, 4))
    pygame.draw.rect(screen, (255, 247, 176), (x + CAR_W // 2 - 12, y - CAR_H // 2 + 1, 8, 4))

    # escudo
    if getattr(car, "shield", False):
        r = max(CAR_W, CAR_H) // 2 + 6 + int(math.sin(pygame.time.get_ticks() / 90) * 2)
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (120, 200, 255, 90), (r + 2, r + 2), r, 3)
        screen.blit(surf, (x - r - 2, y - r - 2))

    # aura turbo
    if getattr(car, "turbo_timer", 0) > 0:
        r = CAR_H // 2 + 8
        surf = pygame.Surface((CAR_W + 16, CAR_H + 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 200, 80, 80), surf.get_rect(), 3)
        screen.blit(surf, (x - (CAR_W + 16) // 2, y - (CAR_H + 16) // 2))

    # humo si frena o rebota
    if getattr(car, "bounce_timer", 0) > 0:
        rr = 8 + int(math.sin(pygame.time.get_ticks() / 60) * 2)
        pygame.draw.circle(screen, (200, 80, 40), (x, y - CAR_H // 2 - 6), rr)


# ----------------------------------------------------------------- traffic
def draw_traffic_car(screen, t):
    x, y = int(t.x), int(t.y)
    body = pygame.Rect(x - CAR_W // 2, y - CAR_H // 2, CAR_W, CAR_H)
    pygame.draw.rect(screen, t.color, body, border_radius=6)
    pygame.draw.rect(screen, (20, 30, 50),
                     (x - CAR_W // 2 + 5, y - CAR_H // 2 + 8, CAR_W - 10, 18),
                     border_radius=3)
    pygame.draw.rect(screen, (20, 30, 50),
                     (x - CAR_W // 2 + 5, y + CAR_H // 2 - 22, CAR_W - 10, 14),
                     border_radius=3)


# ----------------------------------------------------------------- power-ups
def draw_powerup(screen, p):
    x, y = int(p.x), int(p.y)
    pulse = 1 + math.sin(pygame.time.get_ticks() / 180) * 0.1
    base = int(18 * pulse)
    if p.ptype == "turbo":
        color = YELLOW
        glyph = "T"
    elif p.ptype == "shield":
        color = CYAN
        glyph = "S"
    else:
        color = ORANGE
        glyph = "O"
    s = pygame.Surface((base * 2 + 12, base * 2 + 12), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, 80), (base + 6, base + 6), base + 6)
    pygame.draw.circle(s, color, (base + 6, base + 6), base)
    screen.blit(s, (x - base - 6, y - base - 6))
    font = pygame.font.SysFont("arial", 18, bold=True)
    txt = font.render(glyph, True, (30, 30, 30))
    screen.blit(txt, (x - txt.get_width() // 2, y - txt.get_height() // 2))


# ----------------------------------------------------------------- partículas
def draw_particles(screen, system):
    for p in system.items:
        if p.kind == "line":
            surf = pygame.Surface((p.size, 12), pygame.SRCALPHA)
            surf.fill((*p.color, p.alpha))
            screen.blit(surf, (p.x, p.y))
        else:
            r = max(1, int(p.size * (p.life / p.max_life)))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color, p.alpha), (r, r), r)
            screen.blit(surf, (p.x - r, p.y - r))


# ----------------------------------------------------------------- HUD
def draw_progress(screen, p1_dist, p2_dist):
    bar_x, bar_y, bar_w, bar_h = ROAD_LEFT, 12, ROAD_WIDTH, 8
    bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    bg.fill((255, 255, 255, 40))
    screen.blit(bg, (bar_x, bar_y))
    f1 = min(1.0, p1_dist / FINISH_DISTANCE)
    f2 = min(1.0, p2_dist / FINISH_DISTANCE)
    pygame.draw.rect(screen, RED, (bar_x, bar_y, int(bar_w * f1), bar_h // 2))
    pygame.draw.rect(screen, BLUE, (bar_x, bar_y + bar_h // 2, int(bar_w * f2), bar_h // 2))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x + bar_w - 2, bar_y - 4, 2, bar_h + 8))


def draw_hearts(screen, x, y, lives, max_lives, color=RED):
    for i in range(max_lives):
        cx = x + i * 18
        col = color if i < lives else (70, 70, 70)
        pygame.draw.circle(screen, col, (cx + 4, y + 6), 4)
        pygame.draw.circle(screen, col, (cx + 12, y + 6), 4)
        pygame.draw.polygon(screen, col, [(cx, y + 8), (cx + 16, y + 8), (cx + 8, y + 18)])


def draw_hud(screen, fonts, p1, p2, mode, time_left, distance_for_theme, combo, paused):
    font = fonts["normal"]
    small = fonts["small"]

    # Mejor distancia / tiempo: el HUD muestra estado actual.
    p1_text = f"P1  {int(p1.distance)} m   {p1.display_speed_kmh} km/h"
    p2_text = f"CPU {int(p2.distance)} m   {p2.display_speed_kmh} km/h"
    screen.blit(font.render(p1_text, True, RED), (12, H - 56))
    screen.blit(font.render(p2_text, True, BLUE), (12, H - 32))

    # Vidas
    draw_hearts(screen, W - 90, H - 56, p1.lives, MAX_LIVES, color=RED)
    draw_hearts(screen, W - 90, H - 32, p2.lives, MAX_LIVES, color=BLUE)

    # Modo y reloj
    info_lines = [f"Modo: {mode}"]
    theme = blended_theme(distance_for_theme)
    info_lines.append(f"Tramo: {theme['name']}")
    if mode == "Contrarreloj":
        info_lines.append(f"Tiempo: {max(0.0, time_left):.1f}s")
    elif mode == "Supervivencia":
        info_lines.append(f"Tiempo: {time_left:.1f}s")
    for i, line in enumerate(info_lines):
        screen.blit(small.render(line, True, SUBTEXT), (12, 30 + i * 16))

    # Combo
    if combo >= 2:
        big = fonts["big"]
        txt = big.render(f"x{combo} COMBO", True, YELLOW)
        screen.blit(txt, (W - txt.get_width() - 14, 30))

    # Power-up activo en P1
    badges = []
    if p1.shield: badges.append(("Escudo", CYAN))
    if p1.turbo_timer > 0: badges.append(("Turbo", YELLOW))
    if p1.oil_timer > 0: badges.append(("Aceite!", ORANGE))
    for i, (name, col) in enumerate(badges):
        s = small.render(name, True, col)
        screen.blit(s, (12, H - 80 - i * 16))

    # Ayuda
    help_text = "Flechas mover · Espacio turbo · P pausa · R reiniciar · Esc salir"
    surf = small.render(help_text, True, SUBTEXT)
    screen.blit(surf, (W - surf.get_width() - 12, H - 18))

    if paused:
        draw_overlay(screen, fonts, "Pausa", "Pulsa P para continuar", "")


# ----------------------------------------------------------------- mini-mapa
def draw_minimap(screen, p1, p2):
    """Pequeño mapa vertical en el lado derecho mostrando posición de ambos."""
    mx, my, mw, mh = W - 26, 30, 14, H - 130
    pygame.draw.rect(screen, (20, 20, 20), (mx, my, mw, mh), border_radius=4)
    pygame.draw.rect(screen, (60, 60, 60), (mx, my, mw, mh), 1, border_radius=4)
    f1 = min(1.0, p1.distance / FINISH_DISTANCE)
    f2 = min(1.0, p2.distance / FINISH_DISTANCE)
    y1 = int(my + mh - mh * f1)
    y2 = int(my + mh - mh * f2)
    pygame.draw.rect(screen, RED, (mx + 1, y1 - 2, mw - 2, 4))
    pygame.draw.rect(screen, BLUE, (mx + 1, y2 - 2, mw - 2, 4))
    pygame.draw.rect(screen, (255, 255, 255), (mx, my, mw, 2))  # meta arriba


# ----------------------------------------------------------------- overlays
def draw_overlay(screen, fonts, title, msg, hint):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    t = fonts["big"].render(title, True, TEXT)
    screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 80))
    if msg:
        m = fonts["normal"].render(msg, True, TEXT)
        screen.blit(m, (W // 2 - m.get_width() // 2, H // 2 - 20))
    if hint:
        h = fonts["small"].render(hint, True, SUBTEXT)
        screen.blit(h, (W // 2 - h.get_width() // 2, H // 2 + 30))


def draw_menu(screen, fonts, title, options, selected, footer=""):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    t = fonts["big"].render(title, True, TEXT)
    screen.blit(t, (W // 2 - t.get_width() // 2, 90))
    for i, label in enumerate(options):
        col = YELLOW if i == selected else TEXT
        prefix = "> " if i == selected else "  "
        line = fonts["normal"].render(prefix + label, True, col)
        screen.blit(line, (W // 2 - line.get_width() // 2, 200 + i * 36))
    if footer:
        f = fonts["small"].render(footer, True, SUBTEXT)
        screen.blit(f, (W // 2 - f.get_width() // 2, H - 50))


def draw_countdown(screen, fonts, value):
    big = fonts["huge"]
    if value > 0:
        txt = big.render(str(int(value)), True, YELLOW)
    else:
        txt = big.render("¡YA!", True, GREEN)
    screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - txt.get_height() // 2))
