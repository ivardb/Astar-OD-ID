from heapq import heappush, heappop
from typing import List, Optional, Tuple

from src.Astar.ODProblem import ODProblem
from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class Node:

    def __init__(self, time_step, state, cost, heuristic, parent=None):
        self.state = state
        self.standard = state.is_standard()
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent
        self.time_step = time_step

    def __lt__(self, other):
        return ((self.cost + self.heuristic), self.heuristic) < ((other.cost + other.heuristic), other.heuristic)


def get_path(node: Node) -> List[Tuple[int, AgentPath]]:
    curr = node
    state_path = []
    while curr is not None:
        if curr.standard:
            state_path.insert(0, curr.state)
        curr = curr.parent
    paths = [[] for _ in state_path[0].agents]
    for path in state_path:
        for index, agent in enumerate(path.agents):
            paths[index].append(agent.coords)
    return [(agent.id, AgentPath(path)) for path, agent in zip(paths, state_path[0].agents)]


class Solver:

    def __init__(self, problem: ODProblem, max_cost=None):
        self.problem = problem
        self.max_cost = float("inf") if max_cost is None else max_cost

    def solve(self) -> Optional[List[Tuple[int, AgentPath]]]:
        initial_state = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        if initial_heuristic > self.max_cost:
            return None

        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(0, initial_state, 0, initial_heuristic))
        popped = 0
        while frontier:
            popped += 1
            current = heappop(frontier)
            if popped % 100000 == 0:
                print(f"Count: {popped}, Heuristic: {current.heuristic}, Cost: {current.cost}, F: {current.heuristic + current.cost}")
            if self.problem.is_final(current.state):
                return get_path(current)
            if current.standard:
                if current.state in expanded:
                    continue
                expanded.add(current.state)
            states = self.problem.expand(current.state, current.time_step)
            for state, cost_increase in states:
                if state not in expanded:
                    cost = current.cost + cost_increase
                    heuristic = self.problem.heuristic(state)
                    if cost + heuristic < self.max_cost:
                        node = Node(current.time_step + 1, state, cost, heuristic, current)
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

