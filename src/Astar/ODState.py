from __future__ import annotations

from typing import Tuple, Optional, Iterator, List

from src.util.AgentPath import AgentPath
from src.util.agent import Agent


class ODState:
    def __init__(self, agents: Iterator[Agent], new_agents: Optional[Iterator[Agent]] = None,
                 accumulated_cost: Optional[Iterator[int]] = None, new_accumulated_cost: Optional[Iterator[int]] = None,
                 illegal_moves_set: Optional[List[AgentPath]] = None, time_step: Optional[int] = None):
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

        def get_illegal(illegal_moves):
            return illegal_moves[time_step] if time_step < len(illegal_moves) else illegal_moves[-1]

        self.illegal_size = None

        if len(self.new_agents) == 0 and illegal_moves_set is not None and time_step is not None:
            self.new_agents = tuple(Agent(illegal_moves.agent_id, get_illegal(illegal_moves), illegal_moves.color) for illegal_moves in illegal_moves_set)
            self.illegal_size = len(self.new_agents)
            self.new_accumulated_cost = tuple(0 for _ in range(len(self.new_agents)))

        assert len(self.new_agents) == len(self.new_accumulated_cost)
        assert len(self.agents) == len(self.accumulated_cost)

    def get_next(self) -> Tuple[Agent, int]:
        """
        Returns the next agent without a move as well as its index and its previous accumulated cost
        """
        i = len(self.new_agents)
        return self.agents[i], self.accumulated_cost[i]

    def move_with_agent(self, agent, acc_cost, illegal_moves_set: List[AgentPath], time_step) -> ODState:
        """
        Makes the agent the next intermediary agent with associated acc cost.
        Should be used together with the data retrieved from get_next()
        """
        new_agents = list(self.new_agents)
        new_agents.append(agent)
        new_acc_cost = list(self.new_accumulated_cost)
        new_acc_cost.append(acc_cost)
        return ODState(self.agents, new_agents, self.accumulated_cost, new_acc_cost, illegal_moves_set=illegal_moves_set, time_step=time_step)

    def valid_next(self, new_agent: Agent) -> bool:
        for i, agent in enumerate(self.new_agents):
            # Vertex conflict
            if agent.coords == new_agent.coords:
                return False

            # Swapping conflict
            if agent.coords == self.agents[len(self.new_agents)].coords and new_agent.coords == self.agents[i].coords:
                return False
        return True

    def is_standard(self) -> bool:
        if self.illegal_size is not None:
            return len(self.new_agents) == self.illegal_size
        return len(self.new_agents) == 0

    def __hash__(self) -> int:
        return tuple.__hash__((self.agents, self.new_agents))

    def __eq__(self, other):
        return self.agents == other.agents and self.new_agents == other.new_agents
