from typing import Tuple, Iterable

from src.Astar.ODState import ODState
from src.util.agent import Agent
from src.util.coord import Coord


class ODProblem:

    def __init__(self, grid, agent_ids):
        """
        Grid starts and goals should already be matched
        :param grid: Matched grid
        :param agent_ids: The agents for which to make the problem
        """
        self.grid = grid
        self.agents_ids = agent_ids
        agents = []
        for id in agent_ids:
            start = self.grid.starts[id]
            agents.append(Agent(id, Coord(start.x, start.y), start.color))
        self.initial = ODState(agents)

    def expand(self, parent: ODState) -> Iterable[Tuple[ODState, int]]:
        res = []
        agent, acc = parent.get_next()

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

    def initial_state(self) -> ODState:
        return self.initial

    def is_final(self, state: ODState) -> bool:
        return self.grid.is_final(state.agents)

    def heuristic(self, state: ODState) -> int:
        h = 0
        for agent in state.new_agents:
            h += self.grid.get_heuristic(agent.coords, agent.id)
        for j in range(len(state.new_agents), len(state.agents)):
            h += self.grid.get_heuristic(state.agents[j].coords, state.agents[j].id)
        return h
