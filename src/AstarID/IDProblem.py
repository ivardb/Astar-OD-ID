from typing import Optional, List, Tuple, Iterator

from mapfmclient import Problem
from mapfmclient.solution import Solution

from src.Astar.ODProblem import ODProblem
from src.Astar.solver import Solver
from src.util.AgentPath import AgentPath
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
        paths: List[Optional[AgentPath]] = [None for _ in range(len(self.grid.starts))]
        for group in self.groups.groups:
            group_paths = self.solve_group(group)
            if group_paths is None:
                return None
            update(paths, group_paths)
        avoided_conflicts = set()
        conflict = self.find_conflict(paths)
        while conflict is not None:
            combine_groups = True
            a, b, a_group, b_group = conflict

            combo = (a_group.agent_ids, b_group.agent_ids)
            if combo not in avoided_conflicts:
                avoided_conflicts.add(combo)

                # Try giving a priority
                problem = ODProblem(self.grid, a_group, illegal_moves=[paths[i] for i in b_group.agent_ids])
                solver = Solver(problem, max_cost=len(paths[a]))
                solution = solver.solve()
                if solution is not None:
                    combine_groups = False
                    update(paths, solution)
                else:
                    # Give b priority
                    problem = ODProblem(self.grid, b_group, illegal_moves=[paths[i] for i in a_group.agent_ids])
                    solver = Solver(problem, max_cost=len(paths[b]))
                    solution = solver.solve()
                    if solution is not None:
                        combine_groups = False
                        update(paths, solution)
            # Combine groups
            if combine_groups:
                group = self.groups.combine_agents(a, b)
                group_paths = self.solve_group(group)
                if group_paths is None:
                    return None
                update(paths, group_paths)

            # Find next conflict
            conflict = self.find_conflict(paths)
        return AgentPath.to_solution(paths)

    def find_conflict(self, paths: List[AgentPath]) -> Optional[Tuple[int, int, Group, Group]]:
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                if paths[i].conflicts(paths[j]):
                    return i, j, self.groups.group_map[i], self.groups.group_map[j]
        return None

    def solve_group(self, group):
        problem = ODProblem(self.grid, group)
        solver = Solver(problem)
        return solver.solve()


def update(paths, new_paths: Iterator[Tuple[int, AgentPath]]):
    for i, path in new_paths:
        paths[i] = path


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


