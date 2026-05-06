"""Punto de entrada del juego de carreras."""
import sys

from game import Game


def main():
    try:
        Game().run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
