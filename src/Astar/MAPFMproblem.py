from typing import Tuple, Iterable

import mapfmclient

from src.Astar.MAPFMstate import MapfmState
from src.util.agent import Agent
from src.util.coord import Coord
from src.util.grid import Grid


class MapfmProblem:

    def __init__(self, problem: mapfmclient.Problem):
        proper_starts = problem.starts
        proper_goals = problem.goals
        new_goals = []
        for agent in proper_starts:
            for goal in proper_goals:
                if agent.color == goal.color:
                    new_goals.append(goal)
                    proper_goals.remove(goal)
                    break
        proper_goals = new_goals

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
        if parent.valid_next(agent):
            if self.grid.on_goal(agent):
                res.append((parent.move_with_agent(agent, acc + 1), 0))
            else:
                res.append((parent.move_with_agent(agent, 0), 1))
        return res

    def initial_state(self) -> MapfmState:
        return self.initial

    def is_final(self, state: MapfmState) -> bool:
        return self.grid.is_final(state.agents)

    def heuristic(self, state: MapfmState) -> int:
        h = 0
        for i, agent in enumerate(state.new_agents):
            h += self.grid.get_heuristic(agent.coords, i)
        for j in range(len(state.new_agents), len(state.agents)):
            h += self.grid.get_heuristic(state.agents[j].coords, j)
        return h
