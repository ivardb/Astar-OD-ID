from __future__ import annotations

from src.util.coord import Coord


class Agent:
    __slots__ = ("id", "coords", "color")

    def __init__(self, number, coord: Coord, color: int):
        """
        Create an Agent.
        :param number: The agent number/id
        :param coord: The current position
        :param color: The color of the agent
        """
        self.id = number
        self.coords = coord
        self.color = color

    def move(self, dx: int, dy: int) -> Agent:
        """
        Creates a new agent that has moved in the given direction.
        :param dx: The change in the x direction
        :param dy: The change in the y direction
        :return: A moved agent
        """
        return Agent(self.id, self.coords.move(dx, dy), self.color)

    def __eq__(self, other):
        return self.id == other.id and self.coords == other.coords and self.color == other.color

    def __hash__(self):
        return tuple.__hash__((self.id, self.coords, self.color))
