from __future__ import annotations

from typing import Iterator, List

from mapfmclient import Solution

from src.util.coord import Coord


class AgentPath:

    def __init__(self, coords: Iterator[Coord]):
        self.coords = tuple(coords)

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, item):
        return self.coords[item]

    def conflicts(self, other: AgentPath) -> bool:
        n = len(self)
        m = len(other)
        i = 1
        while i < n and i < m:
            if self[i] == other[i]:
                return True
            if self[i-1] == other[i] and self[i] == other[i-1]:
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
        solution = []
        for path in paths:
            solution.append([(coord.x, coord.y) for coord in path.coords])
        return Solution.from_paths(solution)
