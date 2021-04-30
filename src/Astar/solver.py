from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional, Set

from src.Astar.ODProblem import ODProblem
from src.Astar.ODState import ODState
from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class Node:

    def __init__(self, time_step: int, state, cost, heuristic, conflicts: int, parent=None):
        self.state = state
        self.standard = state.is_standard()
        self.cost = cost
        self.heuristic = heuristic
        self.conflicts = conflicts
        self.parent = parent
        self.time_step = time_step
        self.f = self.cost + self.heuristic

    def __lt__(self, other: Node):
        return (self.f, self.conflicts, self.heuristic) \
               < (other.f, other.conflicts, other.heuristic)


def get_path(node: Node) -> List[AgentPath]:
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
    return [AgentPath(agent.id, agent.color, path) for path, agent in zip(paths, state_path[0].agents)]


class Solver:

    def __init__(self, problem: ODProblem, max_cost=None):
        self.problem = problem
        self.max_cost = float("inf") if max_cost is None else max_cost

    def solve(self) -> Optional[List[AgentPath]]:
        initial_state, initial_cost = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        if initial_heuristic + initial_cost > self.max_cost:
            return None

        expanded: Set[ODState] = set()
        seen: Set[ODState] = set()
        frontier: List[Node] = []
        heappush(frontier, Node(0, initial_state, initial_cost, initial_heuristic, 0))
        popped = 0
        while frontier:
            popped += 1
            current = heappop(frontier)
            if popped % 100000 == 0:
                print(f"Count: {popped}, Heuristic: {current.heuristic}, Cost: {current.cost}, F: {current.f}, "
                      f"Frontier size: {len(frontier)}, Seen size: {len(seen)} Expanded Size: {len(expanded)}")
            if self.problem.is_final(current.state):
                return get_path(current)
            if current.standard and current.state in expanded:
                continue
            states = self.problem.expand(current.state, current.time_step)

            put_back = False
            put_back_f = float("inf")
            for state, cost_increase, conflicts in states:
                cost = current.cost + cost_increase
                heuristic = self.problem.heuristic(state)
                if cost + heuristic == current.f:
                    if state in seen:
                        continue
                    node = Node(current.time_step + 1, state, cost, heuristic, current.conflicts + conflicts, current)
                    heappush(frontier, node)
                    seen.add(state)
                elif current.f < cost + heuristic <= self.max_cost:
                    put_back = True
                    put_back_f = min(put_back_f, cost + heuristic)
            if put_back:
                current.f = put_back_f
                heappush(frontier, current)
            elif current.state.is_standard:
                expanded.add(current.state)
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

