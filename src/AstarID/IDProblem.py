from functools import reduce
from typing import Optional, List, Tuple

from mapfmclient import Problem
from mapfmclient.solution import Path, Solution

from src.Astar.ODProblem import ODProblem
from src.Astar.ODState import ODState
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

    def solve(self) -> Optional[Solution]:
        singleton_groups = [Group([n]) for n in range(len(self.grid.starts))]
        super_group = reduce(lambda a, b: a.combine(b), singleton_groups, Group([]))
        problem = ODProblem(self.grid, super_group)
        solver = Solver(problem)
        paths = solver.solve()
        if paths is None:
            return None
        final_paths = [None for _ in range(len(self.grid.starts))]
        for i, path in paths:
            final_paths[i] = path
        if all(path is not None for path in final_paths):
            return Solution.from_paths(final_paths)
        return None
