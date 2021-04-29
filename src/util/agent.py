from __future__ import annotations

from src.util.coord import Coord


class Agent:

    def __init__(self, number, coord: Coord, color: int):
        self.id = number
        self.coords = coord
        self.color = color

    def move(self, dx: int, dy: int) -> Agent:
        return Agent(self.id, self.coords.move(dx, dy), self.color)

    def __eq__(self, other):
        return self.id == other.id and self.coords == other.coords and self.color == other.color

    def __hash__(self):
        return tuple.__hash__((self.id, self.coords, self.color))
