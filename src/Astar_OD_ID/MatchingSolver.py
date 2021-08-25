from typing import Optional, List, Iterator, Tuple

from mapfmclient import Problem, Solution

from src.Astar_OD_ID.Astar_ID.IDProblem import IDProblem
from src.util.CAT import CAT
from src.util.agent_path import AgentPath
from src.util.grid import HeuristicType, Grid
from src.util.group import Group
from src.util.groups import Groups
from src.util.logger.logger import Logger

logger = Logger("MatchingSolver")


class MatchingSolver:

    def __init__(self, problem: Problem, heuristic_type: HeuristicType = HeuristicType.Exhaustive, enable_sorting=False,
                 enable_matchingID=False):
        """
        Create a problem that uses matching ID, only makes sense for Exhaustive matching.
        :param problem: The problem to solve.
        :param heuristic_type: The heuristic type.
        """
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals, heuristic_type)
        self.heuristic_type = heuristic_type
        self.enable_sorting = enable_sorting
        self.enable_matchingID = enable_matchingID

        if enable_matchingID:
            max_team = max(map(lambda x: x.color, self.grid.starts))
            teams = [list() for _ in range(max_team + 1)]
            for i, start in enumerate(self.grid.starts):
                teams[start.color].append(i)
            self.teams = list(map(Group, filter(lambda x: len(x) > 0, teams)))

    def solve(self, enable_cat: bool = True,upper_bound: Optional[int] = float("inf")) -> Optional[Solution]:
        """
        Solve the problem
        :param enable_cat: Option to disable the Collision Avoidance for this layer. Has no effect on normal ID CAT
        :return: A solution if it exists.
        """
        if not self.enable_matchingID:
            id_problem = IDProblem(self.grid, self.heuristic_type, Group(list(range(len(self.grid.starts)))),
                                   enable_sorting=self.enable_sorting)
            paths = id_problem.solve(upper_bound=upper_bound)
            if paths is None:
                return None
            return AgentPath.to_solution(paths)
        path_set = GroupPathSet(list(range(len(self.grid.starts))), self.grid.w, self.grid.h, self.teams, enable_cat)
        for group in path_set.groups.groups:
            logger.log(f"Solving agents: {group}")
            id_problem = IDProblem(self.grid, self.heuristic_type, group, enable_sorting=self.enable_sorting)
            paths = id_problem.solve(cat=path_set.cat)
            if paths is None:
                return None
            path_set.update(paths)
        conflict = path_set.find_conflict()
        while conflict is not None:
            a, b = conflict
            new_group = path_set.groups.combine_agents(a, b)
            logger.log(f"Solving agents: {new_group}")
            id_problem = IDProblem(self.grid, self.heuristic_type, new_group, enable_sorting=self.enable_sorting)
            paths = id_problem.solve(cat=path_set.cat)
            if paths is None:
                return None
            path_set.update(paths)
            conflict = path_set.find_conflict()
        return AgentPath.to_solution(path_set.paths)


class GroupPathSet:

    def __init__(self, agent_ids, w, h, teams: List[Group], enable_cat):
        """
        Create a path set used to track the paths for MatchingID.
        :param agent_ids: The agent_ids
        :param w: The width of the grid
        :param h: The height of the grid
        :param teams: The teams
        :param enable_cat: If CAT should be used
        """
        self.groups = Groups(teams)
        self.remove_one_groups()
        self.paths: List[Optional[AgentPath]] = [None for _ in range(len(agent_ids))]
        self.cat = CAT(agent_ids, w, h) if enable_cat else CAT.empty()

    def update(self, new_paths: Iterator[AgentPath]):
        """
        Update the stored paths with the new paths.
        :param new_paths: The new paths
        """
        for path in new_paths:
            i = path.agent_id
            self.cat.remove_cat(self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(path)

    def find_conflict(self) -> Optional[Tuple[int, int]]:
        """
        Finds a conflict among the stored paths.
        :return: The first found conflict.
        """
        for i in range(len(self.paths)):
            for j in range(i + 1, len(self.paths)):
                if self.paths[i].conflicts(self.paths[j]):
                    return i, j
        return None

    def remove_one_groups(self):
        """
        Method to merge groups of size 1 as solving those separately never leads to a performance increase.
        """
        one_group_agents = list()
        for group in self.groups:
            if len(group) == 1:
                one_group_agents.append(group[0])
        for i in range(1, len(one_group_agents)):
            self.groups.combine_agents(one_group_agents[0], one_group_agents[i])
