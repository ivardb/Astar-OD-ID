from heapq import heappush, heappop
from typing import List, Optional

from src.Astar.ODProblem import ODProblem
from src.Astar.ODState import ODState
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


def get_path(node: Node) -> List[ODState]:
    curr = node
    path = []
    while curr is not None:
        if curr.standard:
            path.insert(0, curr.state)
        curr = curr.parent
    return path


class Solver:

    def __init__(self, problem: ODProblem):
        self.problem = problem

    def solve(self) -> Optional[List[ODState]]:
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

