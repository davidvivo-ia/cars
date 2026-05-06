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
