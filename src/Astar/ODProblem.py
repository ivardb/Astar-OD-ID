from typing import Tuple, Iterable, List, Set

from src.Astar.ODState import ODState
from src.util.CAT import CAT
from src.util.AgentPath import AgentPath
from src.util.agent import Agent
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class ODProblem:

    def __init__(self, grid: Grid, assigned_goals, group: Group, cat: CAT, illegal_moves: List[AgentPath] = None):
        self.grid = grid
        self.agent_ids = group.agent_ids
        self.assigned_goals = assigned_goals
        agents = []
        if illegal_moves is not None:
            for moves in illegal_moves:
                agents.append(Agent(moves.agent_id, moves[0], moves.color))
        for id in self.agent_ids:
            start = grid.starts[id]
            agents.append(Agent(id, Coord(start.x, start.y), start.color))
        self.initial = ODState(agents, illegal_moves_set=illegal_moves, time_step=1)
        self.illegal_moves = illegal_moves
        self.cat = cat

    def expand(self, parent: ODState, current_time) -> Iterable[Tuple[ODState, int, int]]:
        """

        :rtype: List of new_states, expand_cost and conflicts
        """
        res = []
        agent, acc = parent.get_next()

        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_agent = agent.move(dx, dy)
            if not self.grid.is_walkable(new_agent.coords):
                continue
            if not parent.valid_next(new_agent):
                continue
            res.append((parent.move_with_agent(new_agent, 0, self.illegal_moves, current_time + 1), acc + 1, self.cat.get_cat(self.agent_ids, new_agent.coords)))
        # Add standing still as option
        if parent.valid_next(agent):
            if self.grid.on_goal(agent):
                res.append((parent.move_with_agent(agent, acc + 1, self.illegal_moves, current_time + 1), 0, self.cat.get_cat(self.agent_ids, new_agent.coords)))
            else:
                res.append((parent.move_with_agent(agent, 0, self.illegal_moves, current_time + 1), 1, self.cat.get_cat(self.agent_ids, new_agent.coords)))
        return res

    def initial_state(self) -> ODState:
        return self.initial

    def is_final(self, state: ODState) -> bool:
        return self.grid.is_final(state.agents)

    def heuristic(self, state: ODState) -> int:
        h = 0
        for agent in state.new_agents:
            h += self.grid.get_heuristic(agent.coords, self.assigned_goals[agent.id])
        for j in range(len(state.new_agents), len(state.agents)):
            h += self.grid.get_heuristic(state.agents[j].coords, self.assigned_goals[state.agents[j].id])
        return h
