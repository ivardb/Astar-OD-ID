from typing import List, Optional, Iterator, Tuple

from src.util.AgentPath import AgentPath
from src.util.CAT import CAT
from src.util.coord import Coord
from src.util.grid import Grid, HeuristicType


class PathSet:

    def __init__(self, grid: Grid, agent_ids: List[int], heuristic_type: HeuristicType, assigned_goals: dict = None):
        """
        Create a PathSet to keep track of paths and calculate costs etc.
        :param grid: The grid the paths are in.
        :param agent_ids: The agent_ids that are stored here.
        :param heuristic_type: THe type of heuristic used.
        :param assigned_goals: The goals for each of the given agent_ids
        """
        self.grid = grid
        self.heuristic_type = heuristic_type
        self.agent_ids = agent_ids
        self.mapping = dict((id, i) for i, id in enumerate(agent_ids))
        if heuristic_type == HeuristicType.Exhaustive:
            self.assigned_goals = assigned_goals
        self.paths: List[Optional[AgentPath]] = [None for _ in range(len(agent_ids))]
        self.costs: List[Optional[int]] = [None for _ in range(len(agent_ids))]
        self.cat = CAT(agent_ids, grid.w, grid.h)

    def update(self, new_paths: Iterator[AgentPath]):
        """
        Updates the paths in the internal storage.
        Should always be used as the internal index is not the same as the id.
        :param new_paths: The new_paths
        """
        for path in new_paths:
            i = self.mapping[path.agent_id]
            self.cat.remove_cat(self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(path)
            self.costs[i] = path.get_cost()

    def get_remaining_cost(self, indexes: List[int], max_cost) -> int:
        """
        Calculates the remaining cost that can be spent on a set of paths without going over the max cost
        :param indexes: The ids that still need to be solved
        :param max_cost: The maximum cost that can't be overridden
        """
        return max_cost - sum(self.get_cost(i) for i in self.agent_ids if i not in indexes)

    def get_cost(self, agent_id):
        """
        Calculate the cost for the id.
        :param agent_id: The id
        :return: The cost
        """
        return self.costs[self.mapping[agent_id]] if self.costs[self.mapping[agent_id]] is not None else self.get_heuristic(agent_id)

    def get_heuristic(self, agent_id):
        """
        Get the heuristic for the id.
        This is the minimum cost a path for this agent will take based on the heuristic.
        Depends on the earlier given heuristic_type.
        :param agent_id: The id
        :return: The minimum heuristic cost
        """
        coord = Coord(self.grid.starts[agent_id].x, self.grid.starts[agent_id].y)
        if self.heuristic_type == HeuristicType.Exhaustive:
            return self.grid.get_heuristic(coord, self.assigned_goals[agent_id])
        else:
            return self.grid.get_heuristic(coord, self.grid.starts[agent_id].color)

    def find_conflict(self) -> Optional[Tuple[int, int]]:
        """
        Find conflicting paths
        :return: ids of conflicting paths
        """
        for i in range(len(self.agent_ids)):
            id_i = self.agent_ids[i]
            path_index_i = self.mapping[id_i]
            for j in range(i + 1, len(self.agent_ids)):
                id_j = self.agent_ids[j]
                path_index_j = self.mapping[id_j]
                if self.paths[path_index_i].conflicts(self.paths[path_index_j]):
                    return id_i, id_j
        return None

    def __getitem__(self, agent_id):
        """
        Should always be used to get a path as internal index differs from id.
        :param agent_id: The id to get the path for
        :return: The path belonging to this id
        """
        return self.paths[self.mapping[agent_id]]
