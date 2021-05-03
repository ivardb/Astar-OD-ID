from queue import Queue
from typing import List, Optional, Iterator

from mapfmclient import MarkedLocation

from src.util.agent import Agent
from src.util.coord import Coord


class Grid:

    def __init__(self, grid: List[List[int]], width: int, height: int,  starts: List[MarkedLocation],
                 goals: List[MarkedLocation], compute_heuristics=False):
        self.grid = grid
        self.w = width
        self.h = height
        self.starts = starts
        self.goals = goals
        self.heuristics = None
        if compute_heuristics:
            self.compute_heuristics()

    def compute_heuristics(self):
        self.heuristics = [self.compute_heuristic(goal.x, goal.y) for goal in self.goals]

    # Calculates the distance to the coordinates for every reachable position
    def compute_heuristic(self, x, y) -> List[List[Optional[int]]]:
        queue = Queue()
        visited = set()
        heuristic = [[None for _ in range(self.w)] for _ in range(self.h)]

        queue.put((Coord(x, y), 0))
        while not queue.empty():
            coord, dist = queue.get()
            if coord in visited:
                continue
            visited.add(coord)

            # Already has a better distance
            if heuristic[coord.y][coord.x] is not None:
                continue
            heuristic[coord.y][coord.x] = dist

            for neighbor in self.get_neighbors(coord):
                if neighbor not in visited:
                    queue.put((neighbor, dist + 1))
        return heuristic

    def get_neighbors(self, coords: Coord):
        res = list()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_coord = coords.move(dx, dy)
            if self.is_walkable(new_coord):
                res.append(new_coord)
        return res

    def get_heuristic(self, coord, goal_index: int) -> Optional[int]:
        if self.heuristics is None:
            self.compute_heuristics()
        return self.heuristics[goal_index][coord.y][coord.x]

    def is_walkable(self, coord) -> bool:
        return 0 <= coord.x < self.w and 0 <= coord.y < self.h and not self.is_wall(coord)

    def is_wall(self, coord) -> bool:
        return self.grid[coord.y][coord.x] == 1

    def is_final(self, agents: Iterator[Agent]) -> bool:
        return all(self.on_goal(agent) for agent in agents)

    def on_goal(self, agent: Agent):
        for goal in self.goals:
            if agent.color == goal.color and agent.coords.x == goal.x and agent.coords.y == goal.y:
                return True
        return False
