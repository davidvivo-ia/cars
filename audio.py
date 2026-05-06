"""Sonidos sintetizados sin dependencias externas.

Genera ondas (cuadradas, dientes de sierra, ruido blanco) en bytes crudos y
los pasa a pygame.mixer.Sound. No hace falta numpy ni archivos .wav.
"""
import math
import random
import struct

import pygame

from config import AUDIO_ENABLED, SAMPLE_RATE


_initialised = False
_sounds: dict = {}
_engine_channel = None


def _pack_stereo(samples):
    return b"".join(struct.pack("<hh", s, s) for s in samples)


def _square(freq, duration, volume=0.4):
    n = int(duration * SAMPLE_RATE)
    period = max(2, int(SAMPLE_RATE / max(freq, 1)))
    half = period // 2
    amp = int(32767 * volume)
    samples = [(amp if (i % period) < half else -amp) for i in range(n)]
    return pygame.mixer.Sound(buffer=_pack_stereo(samples))


def _sweep(f0, f1, duration, volume=0.4, kind="square"):
    n = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    amp = int(32767 * volume)
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        phase += (2 * math.pi * f) / SAMPLE_RATE
        if kind == "saw":
            v = ((phase / math.pi) % 2) - 1
        else:
            v = 1 if math.sin(phase) > 0 else -1
        # envelope (fade out)
        env = 1.0 - t * 0.5
        samples.append(int(amp * v * env))
    return pygame.mixer.Sound(buffer=_pack_stereo(samples))


def _noise(duration, volume=0.5, decay=True):
    n = int(duration * SAMPLE_RATE)
    amp = 32767 * volume
    samples = []
    for i in range(n):
        env = (1 - i / n) if decay else 1.0
        v = (random.random() * 2 - 1) * env
        samples.append(int(amp * v))
    return pygame.mixer.Sound(buffer=_pack_stereo(samples))


def init():
    global _initialised, _engine_channel
    if _initialised or not AUDIO_ENABLED:
        return
    try:
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
        pygame.mixer.init()
    except pygame.error:
        return
    _sounds["beep"] = _sweep(880, 1320, 0.12, 0.35)
    _sounds["powerup"] = _sweep(440, 1100, 0.18, 0.4)
    _sounds["turbo"] = _sweep(220, 700, 0.35, 0.35, kind="saw")
    _sounds["shield"] = _sweep(660, 880, 0.25, 0.35)
    _sounds["crash"] = _noise(0.35, 0.6)
    _sounds["finish"] = _sweep(440, 1200, 0.5, 0.5)
    _sounds["countdown"] = _square(660, 0.12, 0.4)
    _sounds["go"] = _sweep(660, 1320, 0.3, 0.5)
    _sounds["combo"] = _sweep(900, 1500, 0.1, 0.3)
    _engine_channel = pygame.mixer.Channel(7)
    _initialised = True


def play(name: str):
    if not _initialised:
        return
    s = _sounds.get(name)
    if s is not None:
        s.play()


def stop_all():
    if _initialised:
        pygame.mixer.stop()
