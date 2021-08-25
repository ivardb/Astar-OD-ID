from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional

from src.Astar_OD_ID.Astar_OD.ODProblem import ODProblem
from src.Astar_OD_ID.Astar_OD.ODState import ODState
from src.util.agent_path import AgentPath
from src.util.coord import Coord
from src.util.logger.logger import Logger

logger = Logger("Solver")


class Node:
    __slots__ = ("state", "cost", "heuristic", "conflicts", "time_step", "parent")

    def __init__(self, time_step: int, state: ODState, cost, heuristic, conflicts: int, parent=None):
        """
        Construct a node.
        :param time_step: The current time_step
        :param state: The state
        :param cost: The cost so far
        :param heuristic: The heuristic of the state
        :param conflicts: The number of conflicts so far
        :param parent: The parent node
        """
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.conflicts = conflicts
        self.time_step = time_step
        self.parent = parent

    def get_path(self) -> List[AgentPath]:
        """
        Return the path that lead to this node.
        :return: The path from the root node to this node.
        """
        curr = self
        state_path = []
        while curr is not None:
            if curr.state.is_standard():
                state_path.insert(0, curr.state)
            curr = curr.parent
        paths = [[] for _ in state_path[0].agents]
        for path in state_path:
            for index, agent in enumerate(path.agents):
                paths[index].append(agent.coords)
        return [AgentPath(agent.id, agent.color, path) for path, agent in zip(paths, state_path[0].agents)]

    def __lt__(self, other: Node):
        """
        Sorts on cost + heuristic with conflicts and heuristic as tiebreaks.
        :param other: The node to compare to
        :return: If this node is smaller
        """
        return (self.cost + self.heuristic, self.conflicts, self.heuristic) \
               < (other.cost + other.heuristic, other.conflicts, other.heuristic)


class ODSolver:

    def __init__(self, problem: ODProblem, max_cost=None):
        """
        Create a OD A* solver.
        :param problem: The problem to solve.
        :param max_cost: The maximum cost allowed.
        """
        self.problem = problem
        self.max_cost = float("inf") if max_cost is None else max_cost

    def solve(self) -> Optional[List[AgentPath]]:
        """
        Solve the given problem.
        :return: A list of non-conflicting path for all agents if a solution exists, otherwise None
        """
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
                logger.log(f"Count: {popped}, Heuristic: {current.heuristic}, Cost: {current.cost}, "
                           f"F: {current.cost + current.heuristic}, Frontier size: {len(frontier)}, "
                           f"Max: {self.max_cost}")
            if self.problem.is_final(current.state):
                return current.get_path()
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
                        node = Node(current.time_step + 1, state, cost, heuristic, current.conflicts + conflicts,
                                    current)
                        heappush(frontier, node)
        return None

    def pretty_print(self, state):
        """
        Pretty print the state.
        :param state: The state to print on the grid
        """
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
