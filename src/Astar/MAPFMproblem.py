import itertools
from typing import Tuple, Iterable, List

import mapfmclient

from src.Astar.MAPFMstate import MapfmState
from src.util.agent import Agent
from src.util.grid import Grid
from src.util.coord import Coord


class MapfmProblem:

    def __init__(self, problem: mapfmclient.Problem):
        proper_starts = problem.starts
        proper_goals = [next(filter(lambda g: g.color == start.color, problem.goals)) for start in proper_starts]
        self.grid = Grid(problem.grid, problem.width, problem.height, proper_starts, proper_goals,
                         compute_heuristics=True)
        self.initial = MapfmState(map(lambda i: Agent(Coord(i.x, i.y), i.color), self.grid.starts))

    def expand(self, parent: MapfmState) -> Iterable[Tuple[MapfmState, int]]:
        res = []
        i, agent, acc = parent.get_next()

        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_agent = agent.move(dx, dy)
            if not self.grid.is_walkable(new_agent.coords):
                continue
            if not parent.valid_next(new_agent):
                continue
            res.append((parent.move_with_agent(new_agent, 0), acc + 1))
        new_agent = agent.move(0, 0)
        if parent.valid_next(new_agent):
            if self.grid.on_goal(new_agent):
                res.append((parent.move_with_agent(new_agent, acc + 1), 0))
            else:
                res.append((parent.move_with_agent(new_agent, 0), 1))
        return res

    def initial_state(self) -> MapfmState:
        return self.initial

    def is_final(self, state: MapfmState) -> bool:
        return self.grid.is_final(state.agents)

    def heuristic(self, state: MapfmState) -> int:
        h = 0
        for i, agent in enumerate(state.agents):
            h += self.grid.get_heuristic(agent.coords, i)
        return h
