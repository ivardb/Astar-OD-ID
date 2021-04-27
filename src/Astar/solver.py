from heapq import heappush, heappop
from typing import List, Optional, Tuple

from mapfmclient.solution import Path

from src.Astar.ODProblem import ODProblem
from src.util.agent import Agent
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

    def __init__(self, problem: ODProblem, max_cost=None, illegal_moves=None):
        self.problem = problem
        self.max_cost = float("inf") if max_cost is None else max_cost
        self.illegal_moves: Optional[Path] = illegal_moves

    def solve(self) -> Optional[List[Tuple[int, Path]]]:
        initial_state = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        # TODO: Think about if timestep should also be kept here or if the illegal moves need to be in the state
        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(0, initial_state, 0, initial_heuristic))

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
                    cost = current.cost + cost_increase
                    heuristic = self.problem.heuristic(state)
                    if cost + heuristic < self.max_cost:
                        new_time = current.time_step + 1
                        if self.illegal_moves is not None:
                            for i, agent in enumerate(state.agents):
                                if self.agent_conflicts(current.state.agents[i], agent, new_time):
                                    break
                            else:
                                node = Node(new_time, state, cost, heuristic, current)
                                heappush(frontier, node)
                        else:
                            node = Node(new_time, state, cost, heuristic, current)
                            heappush(frontier, node)
        return None

    def agent_conflicts(self, old_agent: Agent, agent: Agent, time: int) -> bool:
        old_path = self.illegal_moves.route[-1] if time-1 >= len(self.illegal_moves.route) else self.illegal_moves.route[time-1]
        cur_path = self.illegal_moves.route[-1] if time >= len(self.illegal_moves.route) else self.illegal_moves.route[time]
        old_coords = (old_agent.coords.x, old_agent.coords.y)
        cur_coords = (agent.coords.x, agent.coords.y)
        if cur_path == cur_coords:
            return True
        return old_coords == cur_path and cur_coords == old_path

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

