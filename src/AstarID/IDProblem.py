from functools import reduce
from typing import Optional, List, Tuple, Iterator

from mapfmclient import Problem
from mapfmclient.solution import Solution, Path

from src.Astar.ODProblem import ODProblem
from src.Astar.solver import Solver
from src.util.grid import Grid
from src.util.group import Group


class IDProblem:

    def __init__(self, problem: Problem, matched=False):
        proper_starts = problem.starts
        proper_goals = problem.goals
        if not matched:
            new_goals = []
            for agent in proper_starts:
                for goal in proper_goals:
                    if agent.color == goal.color:
                        new_goals.append(goal)
                        proper_goals.remove(goal)
                        break
            proper_goals = new_goals

        self.grid = Grid(problem.grid, problem.width, problem.height, proper_starts, proper_goals,
                         compute_heuristics=True)
        self.groups = Groups([Group([n]) for n in range(len(self.grid.starts))])

    def solve(self) -> Optional[Solution]:
        paths: List[Optional[Path]] = [None for _ in range(len(self.grid.starts))]
        for group in self.groups.groups:
            group_paths = self.solve_group(group)
            if group_paths is None:
                return None
            update(paths, group_paths)
        conflict = find_conflict(paths)
        while conflict is not None:
            a, b = conflict
            group = self.groups.combine_agents(a, b)
            group_paths = self.solve_group(group)
            update(paths, group_paths)
            conflict = find_conflict(paths)
        return Solution.from_paths(paths)

    def solve_group(self, group):
        problem = ODProblem(self.grid, group)
        solver = Solver(problem)
        return solver.solve()


def update(paths, new_paths: Iterator[Tuple[int, Path]]):
    for i, path in new_paths:
        paths[i] = path


def find_conflict(paths: List[Path]) -> Optional[Tuple[int, int]]:
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            if conflicting(paths[i], paths[j]):
                return i, j
    return None


def conflicting(a: Path, b: Path) -> bool:
    n = len(a.route)
    m = len(b.route)
    last_a = a.route[-1]
    last_b = b.route[-1]
    old_a = a.route[0]
    old_b = b.route[0]
    for i in range(1, max(n, m)):
        cur_a = a.route[i] if i < n else last_a
        cur_b = b.route[i] if i < m else last_b
        if cur_a == cur_b:
            return True
        if old_a == cur_b and old_b == cur_a:
            return True
        old_a = cur_a
        old_b = cur_b
    return False


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


