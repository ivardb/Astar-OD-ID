from typing import Optional, List, Tuple, Iterator

import itertools
from mapfmclient import Problem
from mapfmclient.solution import Solution

from src.Astar.ODProblem import ODProblem
from src.Astar.solver import Solver
from src.util.AgentPath import AgentPath
from src.util.CAT import CAT
from src.util.coord import Coord
from src.util.grid import Grid, HeuristicType
from src.util.group import Group


class IDProblem:

    def __init__(self, problem: Problem, heuristic_type: HeuristicType):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals, heuristic_type)
        self.groups = None
        self.assigned_goals = None
        self.heuristic_type = heuristic_type

        if heuristic_type == HeuristicType.Exhaustive:
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
        if self.heuristic_type == HeuristicType.Exhaustive:
            best = float("inf")
            best_solution = None
            for goals in self.assigned_goals:
                print(f"Trying goal assignment of {goals} with maximum cost of {best}")
                solution = self.solve_matching(best, goals)
                if solution is not None:
                    cost = sum(map(lambda x: get_cost(x), solution))
                    if cost < best:
                        best = cost
                        best_solution = solution
            return AgentPath.to_solution(best_solution)
        else:
            solution = self.solve_matching()
            if solution is None:
                return None
            else:
                return AgentPath.to_solution(solution)

    def solve_matching(self, maximum=float("inf"), assigned_goals=None) -> Optional[List[AgentPath]]:
        paths = PathSet(self.grid, len(self.grid.goals), self.heuristic_type, assigned_goals=assigned_goals)
        # Create initial paths for the individual agents. Very quick because of the heuristic used
        self.groups = Groups([Group([n]) for n in range(len(self.grid.starts))])
        for group in self.groups.groups:
            problem = ODProblem(self.grid, group, CAT.empty(), assigned_goals=assigned_goals)
            solver = Solver(problem, max_cost=paths.get_remaining_cost(group.agent_ids, maximum))
            group_paths = solver.solve()
            if group_paths is None:
                return None
            # Update the path and CAT table
            paths.update(group_paths)

        # Start looking for conflicts
        avoided_conflicts = set()
        conflict = self.find_conflict(paths.paths)
        while conflict is not None:
            combine_groups = True
            a, b, a_group, b_group = conflict

            # Check if the conflict has been solved before. If so it has clearly failed
            combo = (a_group.agent_ids, b_group.agent_ids)
            if combo not in avoided_conflicts:
                avoided_conflicts.add(combo)

                # Try rerunning a while the b moves are not possible
                problem = ODProblem(self.grid, a_group, paths.cat,
                                    illegal_moves=[paths[i] for i in b_group.agent_ids], assigned_goals=assigned_goals)

                # The maximum cost that it can have while still being optimal
                maximum_cost = get_cost(paths[a]) + sum(get_cost(paths[i]) for i in b_group.agent_ids)
                solver = Solver(problem, max_cost=maximum_cost)
                solution = solver.solve()
                if solution is not None:
                    # If a solution is found we can update the paths and we don't need to combine anything
                    combine_groups = False
                    paths.update(solution)
                else:
                    # Try redoing b by making a illegal
                    problem = ODProblem(self.grid, b_group, paths.cat,
                                        illegal_moves=[paths[i] for i in a_group.agent_ids],
                                        assigned_goals=assigned_goals)

                    # The maximum cost that it can have while still being optimal
                    maximum_cost = get_cost(paths[b]) + sum(get_cost(paths[i]) for i in a_group.agent_ids)
                    solver = Solver(problem, max_cost=maximum_cost)
                    solution = solver.solve()
                    if solution is not None:
                        # If a solution is found we can update the paths and we don't need to combine anything
                        combine_groups = False
                        paths.update(solution)

            # Combine groups
            if combine_groups:
                group = self.groups.combine_agents(a, b)
                print(f"Combining agents from groups of {a} and {b} into {group.agent_ids}")
                problem = ODProblem(self.grid, group, paths.cat, assigned_goals=assigned_goals)
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
    if i > len(path):
        return cost
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

    def __init__(self, grid: Grid, n, heuristic_type: HeuristicType, assigned_goals=None):
        self.grid = grid
        self.heuristic_type = heuristic_type
        if heuristic_type == HeuristicType.Exhaustive:
            self.assigned_goals = assigned_goals
        self.paths: List[Optional[AgentPath]] = [None for _ in range(n)]
        self.costs: List[Optional[int]] = [None for _ in range(n)]
        self.cat = CAT(n, grid.w, grid.h)

    def update(self, new_paths: Iterator[AgentPath]):
        for path in new_paths:
            i = path.agent_id
            self.cat.remove_cat(i, self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(i, path)
            self.costs[i] = get_cost(path)

    def get_remaining_cost(self, indexes: List[int], max_cost) -> int:
        """
        Calculates the remaining cost that can be spent on a set of paths without going over the max cost
        :param indexes: The paths that still need to be solved
        :param max_cost: The maximum cost that can't be overridden
        """
        return max_cost - sum(self.get_cost(i) for i in range(len(self.costs)) if i not in indexes)

    def get_cost(self, index):
        return self.costs[index] if self.costs[index] is not None else self.get_heuristic(index)

    def get_heuristic(self, index):
        coord = Coord(self.grid.starts[index].x, self.grid.starts[index].y)
        if self.heuristic_type == HeuristicType.Exhaustive:
            return self.grid.get_heuristic(coord, self.assigned_goals[index])
        else:
            return self.grid.get_heuristic(coord, self.grid.starts[index].color)

    def __getitem__(self, item):
        return self.paths[item]
