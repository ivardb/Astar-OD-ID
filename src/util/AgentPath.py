from __future__ import annotations

from typing import Iterator, List

from mapfmclient import Solution

from src.util.coord import Coord


class AgentPath:

    def __init__(self, agent_id: int, color: int, coords: Iterator[Coord]):
        """
        Creates a path for an agent
        :param agent_id: The agent to whom the path belongs
        :param color: The color of that agent
        :param coords: The path coordinates
        """
        self.agent_id = agent_id
        self.color = color
        self.coords = tuple(coords)

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, item):
        return self.coords[item]

    def conflicts(self, other: AgentPath) -> bool:
        """
        Checks if two paths collide.
        :param other: The other path
        :return:True if there is a conflict
        """
        n = len(self)
        m = len(other)
        i = 1
        while i < n and i < m:
            if self[i] == other[i]:
                return True
            if self[i - 1] == other[i] and self[i] == other[i - 1]:
                return True
            i += 1
        while i < n:
            if self[i] == other[-1]:
                return True
            i += 1
        while i < m:
            if other[i] == self[-1]:
                return True
            i += 1
        return False

    @staticmethod
    def to_solution(paths: List[AgentPath]):
        """
        Turns a list of paths into a solution
        :param paths: The paths
        :return: A solution
        """
        solution = []
        for path in paths:
            solution.append([(coord.x, coord.y) for coord in path.coords])
        return Solution.from_paths(solution)

    def get_cost(self):
        """
        Gets the cost of a path.
        The cost is calculated as the length of the path - any standing still on the goal node at the end.
        :return: The cost
        """
        cost = len(self)
        last = self[-1]
        i = 2
        if i > len(self):
            return cost
        while self[-i] == last:
            cost -= 1
            i += 1
            if i > len(self):
                break
        return cost
