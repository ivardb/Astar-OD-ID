from typing import Optional, List

from mapfmclient import Problem

from src.Astar.ODProblem import ODProblem
from src.Astar.ODState import ODState
from src.Astar.solver import Solver
from src.util.grid import Grid


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

    def solve(self) -> Optional[List[ODState]]:
        problem = ODProblem(self.grid, list(range(len(self.grid.starts))))
        solver = Solver(problem)
        return solver.solve()