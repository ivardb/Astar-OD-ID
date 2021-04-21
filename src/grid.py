from queue import Queue
from typing import List, Tuple, Optional

from mapfmclient import MarkedLocation


class Grid:

    def __init__(self, grid: List[List[int]], width: int, height: int, starts: List[MarkedLocation],
                 goals: List[MarkedLocation], compute_heuristics=False):
        self.walls = [[grid[y][x] == 1 for x in range(width)] for y in range(height)]
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

        queue.put(((x, y), 0))
        while not queue.empty():
            pos, dist = queue.get()
            visited.add(pos)
            x, y = pos

            # Already has a better distance
            if heuristic[y][x] is not None and dist >= heuristic[y][x]:
                continue
            heuristic[y][x] = dist

            for neighbor in self.get_neighbors(x, y):
                if neighbor not in visited:
                    queue.put((neighbor, dist + 1))
        return heuristic

    def get_neighbors(self, x, y):
        res = list()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            newX = x + dx
            newY = y + dy
            if 0 <= newX < self.w and 0 <= newY < self.h:
                if not self.walls[newY][newX]:
                    res.append((newX, newY))
        return res

    def get_heuristic(self, x: int, y: int, goal_index: int) -> Optional[int]:
        if self.heuristics is None:
            self.compute_heuristics()
        return self.heuristics[goal_index][y][x]
