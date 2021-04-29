import itertools
from typing import Optional, List, Tuple, Iterator

from mapfmclient import Problem, MarkedLocation
from mapfmclient.solution import Solution

from src.Astar.ODProblem import ODProblem
from src.Astar.solver import Solver
from src.util.AgentPath import AgentPath
from src.util.CAT import CAT
from src.util.coord import Coord
from src.util.grid import Grid
from src.util.group import Group


class IDProblem:

    def __init__(self, problem: Problem):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals,
                         compute_heuristics=True)
        self.groups = None

        goal_ids = []
        for start in problem.starts:
            ids = []
            for i, goal in enumerate(self.grid.goals):
                if start.color == goal.color:
                    ids.append(i)
            ids.sort(key=lambda x: self.grid.get_heuristic(Coord(start.x, start.y), x))
            goal_ids.append(ids)
        self.assigned_goals = filter(lambda x: len(x) == len(set(x)), itertools.product(*goal_ids))

    def solve(self) -> Optional[Solution]:
        best = float("inf")
        best_solution = None
        for goals in self.assigned_goals:
            print(f"Trying goal assignment of {goals} with maximum cost of {best}")
            solution = self.solve_matching(goals, best)
            if solution is not None:
                cost = sum(map(lambda x: get_cost(x), solution))
                if cost < best:
                    best = cost
                    best_solution = solution
        return AgentPath.to_solution(best_solution)

    def solve_matching(self, assigned_goals, maximum) -> Optional[List[AgentPath]]:
        paths = PathSet(self.grid, assigned_goals, len(self.grid.goals))
        self.groups = Groups([Group([n]) for n in range(len(self.grid.starts))])
        for group in self.groups.groups:
            problem = ODProblem(self.grid, assigned_goals, group, CAT.empty())
            solver = Solver(problem, max_cost=paths.get_remaining_cost(group.agent_ids, maximum))
            group_paths = solver.solve()
            if group_paths is None:
                return None
            paths.update(group_paths)
        avoided_conflicts = set()
        conflict = self.find_conflict(paths.paths)
        while conflict is not None:
            combine_groups = True
            a, b, a_group, b_group = conflict

            combo = (a_group.agent_ids, b_group.agent_ids)
            if combo not in avoided_conflicts:
                avoided_conflicts.add(combo)

                # Try giving a priority
                problem = ODProblem(self.grid, assigned_goals, a_group, paths.cat,
                                    illegal_moves=[paths[i] for i in b_group.agent_ids])
                solver = Solver(problem, max_cost=len(paths[a]))
                solution = solver.solve()
                if solution is not None:
                    combine_groups = False
                    paths.update(solution)
                else:
                    # Give b priority
                    problem = ODProblem(self.grid, assigned_goals, b_group, paths.cat,
                                        illegal_moves=[paths[i] for i in a_group.agent_ids])
                    solver = Solver(problem, max_cost=len(paths[b]))
                    solution = solver.solve()
                    if solution is not None:
                        combine_groups = False
                        paths.update(solution)
            # Combine groups
            if combine_groups:
                group = self.groups.combine_agents(a, b)
                print(f"Combining agents from groups of {a} and {b} into {group.agent_ids}")
                problem = ODProblem(self.grid, assigned_goals, group, paths.cat)
                solver = Solver(problem, max_cost=paths.get_remaining_cost(group.agent_ids, maximum))
                group_paths = solver.solve()
                if group_paths is None:
                    return None
                paths.update(group_paths)

            # Find next conflict
            conflict = self.find_conflict(paths.paths)
        return paths.paths

    def find_conflict(self, paths: List[AgentPath]) -> Optional[Tuple[int, int, Group, Group]]:
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                if paths[i].conflicts(paths[j]):
                    return i, j, self.groups.group_map[i], self.groups.group_map[j]
        return None


def get_cost(path: AgentPath):
    cost = len(path)
    last = path[-1]
    i = 2
    while path[-i] == last:
        cost -= 1
        i += 1
        if i > len(path):
            break
    return cost


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


class PathSet:

    def __init__(self, grid: Grid, assigned_goals, n):
        self.grid = grid
        self.assigned_goals = tuple(assigned_goals)
        self.paths: List[Optional[AgentPath]] = [None for _ in range(n)]
        self.costs: List[Optional[int]] = [None for _ in range(n)]
        self.cat = CAT(n, grid.w, grid.h)

    def update(self, new_paths: Iterator[Tuple[int, AgentPath]]):
        for i, path in new_paths:
            self.cat.remove_cat(i, self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(i, path)
            self.costs[i] = get_cost(path)

    def get_remaining_cost(self, indexes: List[int], max_cost: int) -> int:
        """
        Calculates the remaining cost that can be spent on a set of paths without going over the max cost
        :param indexes: The paths that still need to be solved
        :param max_cost: The maximum cost that can't be overridden
        """
        return max_cost - sum(self.get_cost(i) for i in range(len(self.costs)) if i not in indexes)

    def get_cost(self, index):
        return self.costs[index] if self.costs[index] is not None else \
            self.grid.get_heuristic(Coord(self.grid.starts[index].x, self.grid.starts[index].y),
                                    self.assigned_goals[index])

    def __getitem__(self, item):
        return self.paths[item]
