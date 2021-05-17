from typing import Optional

from mapfmclient import Problem, Solution

from src.AstarID.IDProblem import IDProblem
from src.util.grid import HeuristicType, Grid
from src.util.group import Group


class MatchingID:

    def __init__(self, problem: Problem, heuristic_type: HeuristicType):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals, heuristic_type)
        self.heuristic_type = heuristic_type

    def solve(self) -> Optional[Solution]:
        id_problem = IDProblem(self.grid, self.heuristic_type, Group(range(len(self.grid.starts))))
        return id_problem.solve()
