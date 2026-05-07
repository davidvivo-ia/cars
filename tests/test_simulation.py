"""Tests sin pantalla: lógica pura del juego."""
import os
import sys
import unittest

# Permite ejecutar `python -m unittest` desde la raíz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (  # noqa: E402
    CAR_TYPES, DIFFICULTIES, FINISH_DISTANCE, MAX_LIVES, lane_center, LANES,
)
from entities import Car, TrafficCar, ParticleSystem, PowerUp  # noqa: E402
from ai import AIDriver  # noqa: E402
import highscore  # noqa: E402


def _make_car(lane=1, ai=False):
    return Car("test", lane=lane, car_type=CAR_TYPES[0], ai=ai)


class CarTests(unittest.TestCase):
    def test_lane_change_moves_x_toward_target(self):
        c = _make_car(lane=1)
        old_x = c.x
        # mantener pulsado "derecha" varios frames
        for _ in range(20):
            c.update(1.0, (False, True, True, False))
        self.assertGreater(c.x, old_x)
        self.assertEqual(c.lane, 2)

    def test_acceleration_increases_speed(self):
        c = _make_car()
        for _ in range(10):
            c.update(1.0, (False, False, True, False))
        self.assertGreater(c.speed, 0)

    def test_take_hit_reduces_lives_and_bounces(self):
        c = _make_car()
        c.speed = 5.0
        ps = ParticleSystem()
        was_hit = c.take_hit(particles=ps)
        self.assertTrue(was_hit)
        self.assertEqual(c.lives, MAX_LIVES - 1)
        self.assertLess(c.speed, 0)
        self.assertGreater(c.invuln_timer, 0)

    def test_shield_absorbs_hit(self):
        c = _make_car()
        c.shield = True
        c.speed = 5.0
        was_hit = c.take_hit()
        self.assertFalse(was_hit)  # no contó como golpe
        self.assertFalse(c.shield)
        self.assertEqual(c.lives, MAX_LIVES)

    def test_invulnerability_blocks_hit(self):
        c = _make_car()
        c.invuln_timer = 10
        was_hit = c.take_hit()
        self.assertFalse(was_hit)
        self.assertEqual(c.lives, MAX_LIVES)

    def test_three_hits_kills_car(self):
        c = _make_car()
        for _ in range(MAX_LIVES):
            c.invuln_timer = 0
            c.take_hit()
        self.assertEqual(c.lives, 0)
        self.assertFalse(c.alive)

    def test_turbo_increases_max_speed(self):
        c = _make_car()
        c.collect_powerup("turbo")
        # un frame para aplicar
        c.update(1.0, (False, False, True, False))
        self.assertGreater(c.max_speed, c.base_max_speed)


class AITests(unittest.TestCase):
    def test_ai_avoids_obstacle_in_same_lane(self):
        car = _make_car(lane=1, ai=True)
        opp = _make_car(lane=0)
        ai = AIDriver(DIFFICULTIES["Normal"])
        # tráfico justo delante en el mismo carril
        traffic = [TrafficCar(lane=1, speed=2.0, color=(0, 0, 0))]
        traffic[0].y = car.y - 80  # muy cerca por delante
        left, right, up, down = ai.decide(car, traffic, [], opp, dt=1.0)
        self.assertTrue(left or right or down,
                        "La IA debería intentar esquivar o frenar")

    def test_rubberband_when_far_behind(self):
        car = _make_car(lane=1, ai=True)
        opp = _make_car(lane=2)
        opp.distance = 1000  # muy adelantado
        ai = AIDriver(DIFFICULTIES["Normal"])
        # Sin tráfico: la IA debería querer acelerar siempre
        _, _, up, _ = ai.decide(car, [], [], opp, dt=1.0)
        self.assertTrue(up)


class FinishRuleTests(unittest.TestCase):
    """Reglas del modo Carrera: solo se gana cruzando la meta."""

    def _check(self, p1_alive, p1_dist, p2_alive, p2_dist):
        # Replica la lógica de Game._check_finish para Carrera sin instanciar pygame.
        p1 = type("P", (), {})()
        p2 = type("P", (), {})()
        for c, alive, dist in ((p1, p1_alive, p1_dist), (p2, p2_alive, p2_dist)):
            c.alive = alive
            c.distance = dist
            c.finished = False

        if p1.alive and p1.distance >= FINISH_DISTANCE:
            p1.finished = True
        if p2.alive and p2.distance >= FINISH_DISTANCE:
            p2.finished = True

        winner = "ongoing"
        if p1.finished and p2.finished:
            winner = "p1" if p1.distance >= p2.distance else "p2"
        elif p1.finished:
            winner = "p1"
        elif p2.finished:
            winner = "p2"
        elif not p1.alive and not p2.alive:
            winner = None
        return winner

    def test_dead_opponent_does_not_end_race(self):
        # P1 vivo y todavía lejos, P2 eliminado: la carrera continúa.
        self.assertEqual(self._check(True, 1500, False, 800), "ongoing")

    def test_winner_only_by_reaching_finish(self):
        self.assertEqual(self._check(True, FINISH_DISTANCE, True, 1000), "p1")
        self.assertEqual(self._check(True, 1000, True, FINISH_DISTANCE), "p2")

    def test_both_dead_without_finishing_is_no_winner(self):
        self.assertIsNone(self._check(False, 100, False, 200))

    def test_dead_player_cannot_win_by_distance(self):
        # P1 muerto a 2999 m, P2 vivo a 200 m: nadie ha cruzado y P2 sigue corriendo.
        self.assertEqual(self._check(False, FINISH_DISTANCE - 1, True, 200), "ongoing")


class HighscoreTests(unittest.TestCase):
    def test_update_keeps_best_distance(self):
        data = {"Carrera": {"best_distance": 100, "best_time": None}}
        improved = highscore.update_for_run(data, "Carrera", 200, time_s=30)
        self.assertTrue(improved)
        self.assertEqual(data["Carrera"]["best_distance"], 200)
        self.assertEqual(data["Carrera"]["best_time"], 30)

    def test_update_does_not_regress(self):
        data = {"Carrera": {"best_distance": 500, "best_time": 20}}
        improved = highscore.update_for_run(data, "Carrera", 100, time_s=40)
        self.assertFalse(improved)
        self.assertEqual(data["Carrera"]["best_distance"], 500)
        self.assertEqual(data["Carrera"]["best_time"], 20)


if __name__ == "__main__":
    unittest.main()
