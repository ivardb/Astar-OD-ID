from typing import List, Optional, Iterator

from src.util.AgentPath import AgentPath
from src.util.CAT import CAT
from src.util.coord import Coord
from src.util.grid import Grid, HeuristicType


class PathSet:

    def __init__(self, grid: Grid, agent_ids: List[int], heuristic_type: HeuristicType, assigned_goals: dict = None):
        self.grid = grid
        self.heuristic_type = heuristic_type
        self.agent_ids = agent_ids
        self.mapping = dict((id, i) for i, id in enumerate(agent_ids))
        if heuristic_type == HeuristicType.Exhaustive:
            self.assigned_goals = assigned_goals
        self.paths: List[Optional[AgentPath]] = [None for _ in range(len(agent_ids))]
        self.costs: List[Optional[int]] = [None for _ in range(len(agent_ids))]
        self.cat = CAT(len(agent_ids), grid.w, grid.h)

    def update(self, new_paths: Iterator[AgentPath]):
        for path in new_paths:
            i = self.mapping[path.agent_id]
            self.cat.remove_cat(i, self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(i, path)
            self.costs[i] = path.get_cost()

    def get_remaining_cost(self, indexes: List[int], max_cost) -> int:
        """
        Calculates the remaining cost that can be spent on a set of paths without going over the max cost
        :param indexes: The ids that still need to be solved
        :param max_cost: The maximum cost that can't be overridden
        """
        return max_cost - sum(self.get_cost(i) for i in self.agent_ids if i not in indexes)

    def get_cost(self, agent_id):
        return self.costs[self.mapping[agent_id]] if self.costs[
                                                         self.mapping[agent_id]] is not None else self.get_heuristic(
            agent_id)

    def get_heuristic(self, agent_id):
        coord = Coord(self.grid.starts[agent_id].x, self.grid.starts[agent_id].y)
        if self.heuristic_type == HeuristicType.Exhaustive:
            return self.grid.get_heuristic(coord, self.assigned_goals[agent_id])
        else:
            return self.grid.get_heuristic(coord, self.grid.starts[agent_id].color)

    def __getitem__(self, item):
        return self.paths[item]


class Groups:

    def __init__(self, groups):
        self.groups = groups
        self.group_map = dict()
        for group in groups:
            for agent in group.agent_ids:
                self.group_map[agent] = group

    def combine_agents(self, a, b):
        group_a = self.group_map[a]
        group_b = self.group_map[b]
        group = group_a.combine(group_b)
        self.groups.remove(group_a)
        self.groups.remove(group_b)
        self.groups.append(group)
        for agent in group.agent_ids:
            self.group_map[agent] = group
        return group
