from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional

from src.Astar.ODProblem import ODProblem
from src.Astar.ODState import ODState
from src.util.AgentPath import AgentPath
from src.util.coord import Coord


class Node:
    __slots__ = ("state", "cost", "heuristic", "conflicts", "time_step")

    def __init__(self, time_step: int, state: ODState, cost, heuristic, conflicts: int):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.conflicts = conflicts
        self.time_step = time_step

    def __lt__(self, other: Node):
        return (self.cost + self.heuristic, self.conflicts, self.heuristic) \
               < (other.cost + other.heuristic, other.conflicts, other.heuristic)


class Solver:

    def __init__(self, problem: ODProblem, max_cost=None):
        self.problem = problem
        self.max_cost = float("inf") if max_cost is None else max_cost
        self.parents = dict()

    def solve(self) -> Optional[List[AgentPath]]:
        initial_state, initial_cost = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        if initial_heuristic + initial_cost > self.max_cost:
            return None

        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(0, initial_state, initial_cost, initial_heuristic, 0))
        popped = 0
        while frontier:
            popped += 1
            current = heappop(frontier)
            if popped % 100000 == 0:
                print(f"Count: {popped}, Heuristic: {current.heuristic}, Cost: {current.cost}, F: {current.cost + current.heuristic}, Frontier size: {len(frontier)}, Max:{self.max_cost}")
            if self.problem.is_final(current.state):
                return self.get_path(current)
            if current.state.is_standard():
                if current.state in expanded:
                    continue
                expanded.add(current.state)
            states = self.problem.expand(current.state, current.time_step)
            for state, cost_increase, conflicts in states:
                if state not in expanded:
                    cost = current.cost + cost_increase
                    heuristic = self.problem.heuristic(state)
                    if cost + heuristic <= self.max_cost:
                        node = Node(current.time_step + 1, state, cost, heuristic, current.conflicts + conflicts)
                        self.parents[node] = current
                        heappush(frontier, node)
        return None

    def get_path(self, node: Node) -> List[AgentPath]:
        curr = node
        state_path = []
        while curr is not None:
            if curr.state.is_standard():
                state_path.insert(0, curr.state)
            curr = self.parents.get(curr)
        paths = [[] for _ in state_path[0].agents]
        for path in state_path:
            for index, agent in enumerate(path.agents):
                paths[index].append(agent.coords)
        return [AgentPath(agent.id, agent.color, path) for path, agent in zip(paths, state_path[0].agents)]

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

