from heapq import heappush, heappop
from typing import List, Optional, Tuple

from mapfmclient.solution import Path

from src.Astar.ODProblem import ODProblem
from src.util.coord import Coord


class Node:

    def __init__(self, state, cost, heuristic, parent=None):
        self.state = state
        self.standard = state.is_standard()
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


def get_path(node: Node) -> List[Tuple[int, Path]]:
    curr = node
    state_path = []
    while curr is not None:
        if curr.standard:
            state_path.insert(0, curr.state)
        curr = curr.parent
    paths = [[] for _ in state_path[0].agents]
    for path in state_path:
        for index, agent in enumerate(path.agents):
            paths[index].append((agent.coords.x, agent.coords.y))
    return [(agent.id, Path.from_list(path)) for path, agent in zip(paths, state_path[0].agents)]


class Solver:

    def __init__(self, problem: ODProblem):
        self.problem = problem

    def solve(self) -> Optional[List[Tuple[int, Path]]]:
        initial_state = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(initial_state, 0, initial_heuristic))

        while frontier:
            current = heappop(frontier)
            if self.problem.is_final(current.state):
                return get_path(current)
            if current.standard:
                if current.state in expanded:
                    continue
                expanded.add(current.state)
            states = self.problem.expand(current.state)
            for state, cost_increase in states:
                if state not in expanded:
                    node = Node(state, current.cost + cost_increase, self.problem.heuristic(state), current)
                    heappush(frontier, node)
        return None

    def pretty_print(self, state):
        grid = self.problem.grid
        for j in range(grid.h):
            for i in range(grid.w):
                coord = Coord(i, j)
                symbol = '.'
                if grid.is_wall(coord):
                    symbol = '#'
                else:
                    for k, agent in enumerate(state.agents):
                        if agent.coords == coord:
                            symbol = str(k)
                            break
                print(symbol, end='')
            print()
        print()

