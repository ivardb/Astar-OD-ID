from heapq import heappush, heappop
from typing import List, Optional

from src.Astar.problem import AStarProblem, State


class Node:

    def __init__(self, state, cost, heuristic, parent=None):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


def get_path(node: Node) -> List[State]:
    curr = node
    path = []
    while curr is not None:
        path.insert(0, curr.state)
        curr = curr.parent
    return path


class Solver:

    def __init__(self, problem: AStarProblem):
        self.problem = problem

    def solve(self) -> Optional[List[State]]:
        initial_state = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(initial_state, 0, initial_heuristic))

        while frontier:
            current = heappop(frontier)
            if current in expanded:
                continue
            if self.problem.is_final(current.state):
                return get_path(current)

            expanded.add(current)
            states = self.problem.expand(current.state)
            for state, cost_increase in states:
                if state not in expanded:
                    heappush(frontier, Node(state, current.cost + cost_increase, self.problem.heuristic(state), current))
        return None
