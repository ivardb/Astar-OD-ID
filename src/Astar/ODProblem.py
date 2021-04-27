from typing import Tuple, Iterable, List

from src.Astar.ODState import ODState
from src.util.AgentPath import AgentPath
from src.util.agent import Agent
from src.util.coord import Coord
from src.util.group import Group


class ODProblem:

    def __init__(self, grid, group: Group, illegal_moves: List[AgentPath] = None):
        """
        Grid starts and goals should already be matched
        :param grid: Matched grid
        :param group: The group of agents for which to make the problem
        """
        self.grid = grid
        self.agent_ids = group.agent_ids
        agents = []
        for id in self.agent_ids:
            start = self.grid.starts[id]
            agents.append(Agent(id, Coord(start.x, start.y), start.color))
        self.initial = ODState(agents)
        # TODO:Improve performance by creating dictionaries for lookup of both vertex and swapping conflicts
        self.illegal_moves = illegal_moves

    def expand(self, parent: ODState, current_time) -> Iterable[Tuple[ODState, int]]:
        res = []
        agent, acc = parent.get_next()

        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_agent = agent.move(dx, dy)
            if not self.grid.is_walkable(new_agent.coords):
                continue
            if self.illegal(current_time, agent.coords, new_agent.coords):
                continue
            if not parent.valid_next(new_agent):
                continue
            res.append((parent.move_with_agent(new_agent, 0), acc + 1))
        # Add standing still as option
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

    def illegal(self, time: int, old: Coord, new: Coord) -> bool:
        if self.illegal_moves is None:
            return False
        for illegal_path in self.illegal_moves:
            new_path = illegal_path[time] if time < len(illegal_path) else illegal_path[-1]
            old_path = illegal_path[time-1] if time-1 < len(illegal_path) else illegal_path[-1]
            if new == new_path:
                return True
            if new == old_path and old == new_path:
                return True
        return False

