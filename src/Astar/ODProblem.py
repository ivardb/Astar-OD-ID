from typing import Tuple, Iterable, List

from src.Astar.ODState import ODState
from src.util.AgentPath import AgentPath
from src.util.CAT import CAT
from src.util.agent import Agent
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class ODProblem:

    def __init__(self, grid: Grid, group: Group, cat: CAT, illegal_moves: List[AgentPath] = None):
        """
        Creates a problem to be solved by the A*+OD solver
        :param grid: The grid with walls as well as the starting positions and end positions
        :param group: The group of agents to solve
        :param cat: The CAT table to tiebreak on amount of conflicts caused
        :param illegal_moves: Predetermined paths
        """
        self.grid = grid
        self.agent_ids = group.agent_ids

        # The starting agents are the predetermined agents followed by the starting positions of each agent
        agents = []
        if illegal_moves is not None:
            for moves in illegal_moves:
                agents.append(Agent(moves.agent_id, moves[0], moves.color))
        for id in self.agent_ids:
            start = grid.starts[id]
            agents.append(Agent(id, Coord(start.x, start.y), start.color))

        # Create the initial state and add the predetermined moves for the next time_step
        self.initial = ODState(agents, illegal_moves_set=illegal_moves, time_step=0)
        self.illegal_moves = illegal_moves
        self.cat = cat

    def expand(self, parent: ODState, current_time) -> Iterable[Tuple[ODState, int, int]]:
        """
        Create the next states
        :param parent: The current state to expand
        :param current_time: The time belonging to the parent state
        :return: A list of tuples consisting of the states, their added costs and the number of caused conflicts
        """
        res = []
        agent, acc = parent.get_next()

        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_agent = agent.move(dx, dy)
            if not self.grid.is_walkable(new_agent.coords):
                continue
            if not parent.valid_next(new_agent):
                continue
            collisions = self.cat.get_cat(self.agent_ids, new_agent.coords) + self.grid.on_wrong_goal(new_agent)
            state, additional_cost = parent.move_with_agent(new_agent, 0, self.illegal_moves, current_time + 1)
            res.append((state, acc + 1 + additional_cost, collisions))
        # Add standing still as option
        if parent.valid_next(agent):
            if self.grid.on_goal(agent):
                state, additional_cost = parent.move_with_agent(agent, acc + 1, self.illegal_moves, current_time + 1)
                res.append((state, additional_cost, self.cat.get_cat(self.agent_ids, agent.coords)))
            else:
                collisions = self.cat.get_cat(self.agent_ids, agent.coords) + self.grid.on_wrong_goal(agent)
                state, additional_cost = parent.move_with_agent(agent, 0, self.illegal_moves, current_time + 1)
                res.append((state, 1 + additional_cost, collisions))
        return res

    def initial_state(self) -> Tuple[ODState, int]:
        return self.initial, self.initial.construction_cost + len(self.initial.agents)

    def is_final(self, state: ODState) -> bool:
        return self.grid.is_final(state.agents)

    def heuristic(self, state: ODState) -> int:
        h = 0
        for agent in state.new_agents:
            h += self.grid.get_heuristic(agent.coords, agent.color)
        for j in range(len(state.new_agents), len(state.agents)):
            h += self.grid.get_heuristic(state.agents[j].coords, state.agents[j].color)
        return h
