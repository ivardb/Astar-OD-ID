import itertools
from typing import Optional, List, Tuple, Iterator

from mapfmclient import Problem
from mapfmclient.solution import Solution

from src.Astar.ODProblem import ODProblem
from src.Astar.solver import Solver
from src.util.AgentPath import AgentPath
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class IDProblem:

    def __init__(self, problem: Problem):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.goals,
                         compute_heuristics=True)
        self.groups = Groups([Group([n]) for n in range(len(problem.starts))])

        starts = []
        for i, goal in enumerate(self.grid.goals):
            goal_starts = []
            for start in problem.starts:
                if start.color == goal.color:
                    goal_starts.append(start)
            goal_starts.sort(key=lambda x: self.grid.get_heuristic(Coord(x.x, x.y), i))
            starts.append(goal_starts)
        self.starts = filter(lambda x: len(x) == len(set(x)), itertools.product(*starts))

    def get_cost(self, path: AgentPath):
        cost = len(path)
        last = path[-1]
        i = 2
        while path[-i] == last:
            cost -= 1
            i += 1
            if i > len(path):
                break
        return cost

    def solve(self) -> Optional[Solution]:
        best = float("inf")
        best_solution = None
        for start in self.starts:
            solution = self.solve_matching(start, best)
            if solution is not None:
                cost = sum(map(lambda x: self.get_cost(x), solution))
                if cost < best:
                    best = cost
                    best_solution = solution
        return AgentPath.to_solution(best_solution)

    def solve_matching(self, starts, maximum) -> Optional[List[AgentPath]]:
        # TODO: Track costs that the individual searches can have at maximum
        paths: List[Optional[AgentPath]] = [None for _ in range(len(self.grid.goals))]
        for group in self.groups.groups:
            problem = ODProblem(self.grid, starts, group)
            solver = Solver(problem, max_cost=maximum)
            group_paths = solver.solve()
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
                problem = ODProblem(self.grid, starts, a_group, illegal_moves=[paths[i] for i in b_group.agent_ids])
                solver = Solver(problem, max_cost=len(paths[a]))
                solution = solver.solve()
                if solution is not None:
                    combine_groups = False
                    update(paths, solution)
                else:
                    # Give b priority
                    problem = ODProblem(self.grid, starts, b_group, illegal_moves=[paths[i] for i in a_group.agent_ids])
                    solver = Solver(problem, max_cost=len(paths[b]))
                    solution = solver.solve()
                    if solution is not None:
                        combine_groups = False
                        update(paths, solution)
            # Combine groups
            if combine_groups:
                group = self.groups.combine_agents(a, b)
                problem = ODProblem(self.grid, starts, group)
                solver = Solver(problem, max_cost=maximum)
                group_paths = solver.solve()
                if group_paths is None:
                    return None
                update(paths, group_paths)

            # Find next conflict
            conflict = self.find_conflict(paths)
        return paths

    def find_conflict(self, paths: List[AgentPath]) -> Optional[Tuple[int, int, Group, Group]]:
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                if paths[i].conflicts(paths[j]):
                    return i, j, self.groups.group_map[i], self.groups.group_map[j]
        return None


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
