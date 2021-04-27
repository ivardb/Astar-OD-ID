from typing import Tuple, Iterable, List, Set

from src.Astar.ODState import ODState
from src.util.AgentPath import AgentPath
from src.util.agent import Agent
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class ODProblem:

    def __init__(self, grid: Grid, starts,  group: Group, illegal_moves: List[AgentPath] = None, precompute_conflicts=True):
        """
        Grid starts and goals should already be matched
        :param grid: Matched grid
        :param group: The group of agents for which to make the problem
        """
        self.grid = grid
        self.agent_ids = group.agent_ids
        agents = []
        for id in self.agent_ids:
            start = starts[id]
            agents.append(Agent(id, Coord(start.x, start.y), start.color))
        self.initial = ODState(agents)
        self.illegal_moves = illegal_moves
        self.precompute_conflicts = precompute_conflicts
        if precompute_conflicts and illegal_moves is not None:
            self.vertex_conflict = self.compute_vertex_conflict(illegal_moves)
            self.swapping_conflict = self.compute_swapping_conflict(illegal_moves)

    def compute_vertex_conflict(self, illegal_moves_set) -> List[Set[Coord]]:
        max_t = max(map(lambda x: len(x), illegal_moves_set))
        conflicts = [set() for _ in range(max_t)]
        for illegal_moves in illegal_moves_set:
            t = 0
            while t < len(illegal_moves):
                conflicts[t].add(illegal_moves[t])
                t += 1
            while t < max_t:
                conflicts[t].add(illegal_moves[-1])
                t += 1
        return conflicts

    def compute_swapping_conflict(self, illegal_moves_set: List[AgentPath]):
        max_t = max(map(lambda x: len(x), illegal_moves_set))
        conflicts = [set() for _ in range(max_t)]
        for illegal_moves in illegal_moves_set:
            for t in range(1, len(illegal_moves)):
                conflicts[t-1].add((illegal_moves[t], illegal_moves[t-1]))
        return conflicts

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
        if self.precompute_conflicts:
            if new in self.vertex_conflict[time]:
                return True
            if (old, new) in self.swapping_conflict[time]:
                return True
            return False
        else:
            for illegal_path in self.illegal_moves:
                new_path = illegal_path[time] if time < len(illegal_path) else illegal_path[-1]
                old_path = illegal_path[time - 1] if time - 1 < len(illegal_path) else illegal_path[-1]
                if new == new_path:
                    return True
                if new == old_path and old == new_path:
                    return True
            return False
