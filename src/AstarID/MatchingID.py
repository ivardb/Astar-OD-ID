from copy import deepcopy
from typing import Optional, List, Iterator, Tuple

from mapfmclient import Problem, Solution

from src.AstarID.IDProblem import IDProblem
from src.util.AgentPath import AgentPath
from src.util.Groups import Groups
from src.util.grid import HeuristicType, Grid
from src.util.group import Group


class MatchingID:

    def __init__(self, problem: Problem, heuristic_type: HeuristicType):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals, heuristic_type)
        self.heuristic_type = heuristic_type

        max_team = max(map(lambda x: x.color, self.grid.starts))
        teams = [list() for _ in range(max_team + 1)]
        for i, start in enumerate(self.grid.starts):
            teams[start.color].append(i)
        self.teams = list(map(Group, filter(lambda x: len(x) > 0, teams)))

    def solve(self) -> Optional[Solution]:
        path_set = GroupPathSet(len(self.grid.starts), self.teams)
        for group in path_set.groups.groups:
            print(f"MatchingID: Solving agents: {group.agent_ids}")
            id_problem = IDProblem(self.grid, self.heuristic_type, group)
            paths = id_problem.solve()
            if paths is None:
                return None
            path_set.update(paths)
        conflict = path_set.find_conflict()
        while conflict is not None:
            a, b = conflict
            new_group = path_set.groups.combine_agents(a, b)
            print(f"MatchingID: Solving agents: {new_group.agent_ids}")
            id_problem = IDProblem(self.grid, self.heuristic_type, new_group)
            paths = id_problem.solve()
            if paths is None:
                return None
            path_set.update(paths)
            conflict = path_set.find_conflict()
        return AgentPath.to_solution(path_set.paths)


class GroupPathSet:

    def __init__(self, n, teams: List[Group]):
        self.groups = Groups(teams)
        self.remove_one_groups()
        self.paths: List[Optional[AgentPath]] = [None for _ in range(n)]
        self.costs: List[Optional[int]] = [None for _ in range(n)]

    def update(self, new_paths: Iterator[AgentPath]):
        for path in new_paths:
            self.paths[path.agent_id] = path
            self.costs[path.agent_id] = path.get_cost()

    def find_conflict(self) -> Optional[Tuple[int, int]]:
        for i in range(len(self.paths)):
            for j in range(i + 1, len(self.paths)):
                if self.paths[i].conflicts(self.paths[j]):
                    return i, j
        return None

    def remove_one_groups(self):
        one_group_agents = list()
        for group in self.groups.groups:
            if len(group.agent_ids) == 1:
                one_group_agents.append(group.agent_ids[0])
        for i in range(1, len(one_group_agents)):
            self.groups.combine_agents(one_group_agents[0], one_group_agents[i])
