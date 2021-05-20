from typing import List

from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class CAT:

    def __init__(self, n, w, h, active=True):
        """
        Create a Collision Avoidance Tabble.
        :param n: The number of paths in the table
        :param w: The width
        :param h: The height
        :param active: Can be used to disable the table and always return 0
        """
        self.active = active
        self.n = n
        self.cat = [[list() for _ in range(w)] for _ in range(h)]

    def remove_cat(self, index, path: AgentPath):
        """
        Removes the collisions of the given path.
        :param index: The path index in the table
        :param path: The path
        """
        if not self.active:
            return
        if path is None:
            return
        for coord in path.coords:
            self.cat[coord.y][coord.x].remove(index)

    def add_cat(self, index, path: AgentPath):
        """
        Adds the path to the table with the given index.
        :param index: The index of the path
        :param path: The path
        """
        if not self.active:
            return
        for coord in path.coords:
            self.cat[coord.y][coord.x].append(index)

    def get_cat(self, ignored_paths: List[int], coord: Coord) -> int:
        """
        Gets the number of collisions at the coordinates.
        Ignores the indexes in the ignored_paths
        :param ignored_paths: The indexes to ignore
        :param coord: The location to check for conflicts
        :return: The number of found conflicts
        """
        if self.active:
            return sum(i in self.cat[coord.y][coord.x] for i in range(self.n) if i not in ignored_paths)
        return 0

    @staticmethod
    def empty():
        """
        Creates an inactive Collision Avoidance Table.
        :return: An inactive CAT
        """
        return CAT(0, 0, 0, active=False)
