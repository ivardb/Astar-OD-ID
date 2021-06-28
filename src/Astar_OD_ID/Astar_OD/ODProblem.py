from typing import Tuple, Iterable, List

from Astar_OD_ID.Astar_OD.ODState import ODState
from src.util.CAT import CAT
from src.util.agent import Agent
from src.util.agent_path import AgentPath
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class ODProblem:

    def __init__(self, grid: Grid, group: Group, cats: List[CAT], illegal_moves: List[AgentPath] = None,
                 assigned_goals: dict = None):
        """
        Creates a problem to be solved by the A*+OD solver
        :param grid: The grid with walls as well as the starting positions and end positions
        :param group: The group of agents to solve
        :param cats: The CAT tables to tiebreak on amount of conflicts caused
        :param illegal_moves: Predetermined paths
        :param assigned_goals: The goals for each agent
        """
        self.grid = grid
        self.agent_ids = group.agent_ids
        self.assigned_goals = assigned_goals

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
        self.cats = cats

    def expand(self, parent: ODState, current_time) -> Iterable[Tuple[ODState, int, int]]:
        """
        Create the next states
        :param parent: The current state to expand
        :param current_time: The time belonging to the parent state
        :return: A list of tuples consisting of the states, their added costs and the number of caused conflicts
        """
        res = []
        agent, acc = parent.get_next()
        child_time = current_time + 1
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_agent = agent.move(dx, dy)
            if not self.grid.is_walkable(new_agent.coords):
                continue
            if not parent.valid_next(new_agent):
                continue
            state, additional_cost = parent.move_with_agent(new_agent, 0, self.illegal_moves, child_time)
            res.append((state, acc + 1 + additional_cost, self.get_cat(new_agent.coords, child_time)))
        # Add standing still as option
        if parent.valid_next(agent):
            if self.grid.on_goal(agent):
                state, additional_cost = parent.move_with_agent(agent, acc + 1, self.illegal_moves, child_time)
                res.append((state, additional_cost, self.get_cat(agent.coords, child_time)))
            else:
                state, additional_cost = parent.move_with_agent(agent, 0, self.illegal_moves, child_time)
                res.append((state, 1 + additional_cost, self.get_cat(agent.coords, child_time)))
        return res

    def initial_state(self) -> Tuple[ODState, int]:
        """
        Returns the initial state as well as the initial cost.
        The initial cost takes into account the predetermined moves used by ID,
        as well as the initial cost in the mapf.nl cost calculation
        :return: The initial state and the initial cost
        """
        return self.initial, self.initial.construction_cost + len(self.initial.agents)

    def is_final(self, state: ODState) -> bool:
        """
        Checks if the given state is a final state.
        :param state: The state to check
        :return: If the state is final
        """
        return self.grid.is_final(state.agents)

    def heuristic(self, state: ODState) -> int:
        """
        Calculates the heuristic of the state.
        The calculation depends on if specific goals are given or not.
        If goals are assigned the distance to those goals is used as heuristic,
        otherwise the distance to the nearest goal of the same color is used.
        :param state: The state to calculate for.
        :return: The sum of heuristics for all agents in the state.
        """
        h = 0
        if self.assigned_goals is None:
            for agent in state.new_agents:
                h += self.grid.get_heuristic(agent.coords, agent.color)
            for j in range(len(state.new_agents), len(state.agents)):
                h += self.grid.get_heuristic(state.agents[j].coords, state.agents[j].color)
        else:
            for agent in state.new_agents:
                h += self.grid.get_heuristic(agent.coords, self.assigned_goals[agent.id])
            for j in range(len(state.new_agents), len(state.agents)):
                h += self.grid.get_heuristic(state.agents[j].coords, self.assigned_goals[state.agents[j].id])
        return h

    def get_cat(self, coords, time) -> int:
        """
        Calculates the number of collisions at the given coordinates.
        :param coords: Where to check for collisions.
        :return: The number of collisions
        """
        res = 0
        for cat in self.cats:
            res += cat.get_cat(self.agent_ids, coords, time)
        return res
