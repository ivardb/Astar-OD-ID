from typing import List

from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class CAT:

    def __init__(self, n, w, h, active=True):
        self.active = active
        self.n = n
        self.cat = [[list() for _ in range(w)] for _ in range(h)]

    def remove_cat(self, index, path: AgentPath):
        if path is None:
            return
        for coord in path.coords:
            self.cat[coord.y][coord.x].remove(index)

    def add_cat(self, index, path: AgentPath):
        for coord in path.coords:
            self.cat[coord.y][coord.x].append(index)

    def get_cat(self, ignored_paths: List[int], coord: Coord) -> int:
        if self.active:
            return sum(i in self.cat[coord.y][coord.x] for i in range(self.n) if i not in ignored_paths)
        return 0

    @staticmethod
    def empty():
        return CAT(0, 0, 0, active=False)
