from typing import List

from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class CAT:

    def __init__(self, agent_ids, w, h, active=True):
        """
        Create a Collision Avoidance Table.
        :param agent_ids: All possible agent_ids
        :param w: The width
        :param h: The height
        :param active: Can be used to disable the table and always return 0
        """
        self.active = active
        self.agent_ids = agent_ids
        self.cat = [[list() for _ in range(w)] for _ in range(h)]
        self.length = dict()

    def remove_cat(self, path: AgentPath):
        """
        Removes the collisions of the given path.
        :param path: The path
        """
        if not self.active:
            return
        if path is None:
            return
        for i, coord in enumerate(path.coords):
            self.cat[coord.y][coord.x].remove((path.agent_id, i))

    def add_cat(self, path: AgentPath):
        """
        Adds the path to the table.
        :param path: The path
        """
        if not self.active:
            return
        for i, coord in enumerate(path.coords):
            self.cat[coord.y][coord.x].append((path.agent_id, i))
        self.length[path.agent_id] = len(path)

    def get_cat(self, ignored_paths: List[int], coord: Coord, time) -> int:
        """
        Gets the number of collisions at the coordinates.
        Ignores the ids in the ignored_paths
        :param ignored_paths: The ids to ignore
        :param coord: The location to check for conflicts
        :param time: The time for which to check
        :return: The number of found conflicts
        """
        collision = 0
        if self.active:
            for key, value in self.length.items():
                if time > value:
                    if (key, value) in self.cat[coord.y][coord.x]:
                        collision += 1
            for agent_id in self.agent_ids:
                if agent_id in ignored_paths:
                    continue
                if (agent_id, time) in self.cat[coord.y][coord.x]:
                    collision += 1
        return collision

    @staticmethod
    def empty():
        """
        Creates an inactive Collision Avoidance Table.
        :return: An inactive CAT
        """
        return CAT([], 0, 0, active=False)
