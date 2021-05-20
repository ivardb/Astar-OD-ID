from __future__ import annotations

from typing import Tuple, Optional, Iterator, List

from src.util.AgentPath import AgentPath
from src.util.agent import Agent


class ODState:
    __slots__ = ("agents", "new_agents", "accumulated_cost", "new_accumulated_cost", "illegal_size", "construction_cost")

    def __init__(self, agents: Iterator[Agent], new_agents: Optional[Iterator[Agent]] = None,
                 accumulated_cost: Optional[Iterator[int]] = None, new_accumulated_cost: Optional[Iterator[int]] = None,
                 illegal_moves_set: Optional[List[AgentPath]] = None, time_step: Optional[int] = None):
        """
        Create a state object as used by the A*+OD solver
        :param agents: The agents in their pre-move state
        :param new_agents: The agents in their post-move state.
        :param accumulated_cost: The accumulated cost for each agent
        :param new_accumulated_cost:  The accumulated cost for each post-move agent
        :param illegal_moves_set: Set of predetermined paths.
                Are added to the state when necessary to simplify conflict detection with these paths
        :param time_step: The time step we are in
        """
        self.agents = tuple(agents)

        # If enough intermediary states make them permanent
        self.new_agents = () if new_agents is None else tuple(new_agents)
        if len(self.new_agents) == len(self.agents):
            self.agents = self.new_agents
            self.new_agents = ()
        self.accumulated_cost: Tuple[int] = tuple(0 for _ in self.agents) if accumulated_cost is None else tuple(
            accumulated_cost)

        # If enough intermediary costs make them permanent
        self.new_accumulated_cost = () if new_accumulated_cost is None else tuple(new_accumulated_cost)
        if len(self.new_accumulated_cost) == len(self.accumulated_cost):
            self.accumulated_cost = self.new_accumulated_cost
            self.new_accumulated_cost = ()

        # Named lambda for getting the move from the illegal_moves at the correct time step
        def get_illegal(illegal_moves):
            return illegal_moves[time_step + 1] if time_step + 1 < len(illegal_moves) else illegal_moves[-1]

        self.illegal_size = 0

        # This cost reflects the cost of the predetermined moves
        self.construction_cost = 0

        # If we have a standard state make the predetermined/illegal moves,
        # this way the valid_next method will automatically check for conflicts
        if len(self.new_agents) == 0 and illegal_moves_set is not None and time_step is not None:
            self.new_agents = tuple(Agent(illegal_moves.agent_id, get_illegal(illegal_moves), illegal_moves.color) for illegal_moves in illegal_moves_set)
            self.illegal_size = len(self.new_agents)

            # Calculate the cost of the predetermined moves
            acc_costs = []
            for i, agent in enumerate(self.new_agents):
                # Agent has moves so cost of 1 + accumulated cost
                if agent.coords != self.agents[i].coords:
                    self.construction_cost += 1 + self.accumulated_cost[i]
                    acc_costs.append(0)
                else:
                    # Agent is on goal node so increase the accumulated cost
                    if illegal_moves_set[i][-1] == agent.coords:
                        acc_costs.append(1 + self.accumulated_cost[i])
                    else:
                        # Agent is waiting on non-goal node, so increase cost by 1 as no accumulated cost can exist
                        self.construction_cost += 1
                        acc_costs.append(0)
            self.new_accumulated_cost = tuple(acc_costs)

        assert len(self.new_agents) == len(self.new_accumulated_cost)
        assert len(self.agents) == len(self.accumulated_cost)

    def get_next(self) -> Tuple[Agent, int]:
        """
        Returns the next agent without a move as well as its index and its previous accumulated cost
        """
        i = len(self.new_agents)
        return self.agents[i], self.accumulated_cost[i]

    def move_with_agent(self, agent, acc_cost, illegal_moves_set: List[AgentPath], time_step) -> Tuple[ODState, int]:
        """
        Makes the agent the next intermediary agent with associated acc cost.
        Should be used together with the data retrieved from get_next()
        """
        new_agents = list(self.new_agents)
        new_agents.append(agent)
        new_acc_cost = list(self.new_accumulated_cost)
        new_acc_cost.append(acc_cost)
        state = ODState(self.agents, new_agents, self.accumulated_cost, new_acc_cost, illegal_moves_set=illegal_moves_set, time_step=time_step)
        return state, state.construction_cost

    def valid_next(self, new_agent: Agent) -> bool:
        """
        Verifies if the given agent would cause conflicts with the current agents.
        :param new_agent: The agent to check for.
        :return: True if no conflicts would be caused.
        """
        for i, agent in enumerate(self.new_agents):
            # Vertex conflict
            if agent.coords == new_agent.coords:
                return False

            # Swapping conflict
            if agent.coords == self.agents[len(self.new_agents)].coords and new_agent.coords == self.agents[i].coords:
                return False
        return True

    def is_standard(self) -> bool:
        """
        Returns if the state is standard or intermediate.
        :return: True if the state is standard.
        """
        # A state is standard if either there are no non-predetermined post_move agents
        return len(self.new_agents) == self.illegal_size

    def __hash__(self) -> int:
        return tuple.__hash__((self.agents, self.new_agents))

    def __eq__(self, other):
        return self.agents == other.agents and self.new_agents == other.new_agents
