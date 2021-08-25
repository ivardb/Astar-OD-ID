from heapq import heappush, heappop
from typing import Optional, List

import itertools

from src.Astar_OD_ID.Astar_OD.ODProblem import ODProblem
from src.Astar_OD_ID.Astar_OD.ODSolver import ODSolver
from src.util.CAT import CAT
from src.util.agent_path import AgentPath
from src.util.coord import Coord
from src.util.grid import Grid, HeuristicType
from src.util.group import Group
from src.util.groups import Groups
from src.util.logger.logger import Logger
from src.util.path_set import PathSet

logger = Logger("IDProblem")


class Matching:

    def __init__(self, goals, cost):
        """
        Create a matching object for sorting in priority queue.
        :param goals: The goal assignment
        :param cost: The cost, used for sorting
        """
        self.goals = goals
        self.cost = cost

    def __lt__(self, other):
        """
        Compares the costs
        :param other: The other Matching
        :return: If this one is smaller
        """
        return self.cost < other.cost


class IDProblem:

    def __init__(self, grid: Grid, heuristic_type: HeuristicType, group: Group, enable_sorting=False, pq_size=100):
        """
        Create an A*+ID+OD problem.
        :param grid: The grid of the problem.
        :param heuristic_type: The type of heuristic to use.
        :param group: The subgroup of agents to solve the problem for.
        """
        self.grid = grid
        self.assigned_goals = None
        self.heuristic_type = heuristic_type
        self.agent_ids = group.agent_ids
        self.enable_sorting = enable_sorting

        # Generate iterator with all possible matchings
        if heuristic_type == HeuristicType.Exhaustive:
            self.pq_size = pq_size
            goal_ids = []
            for agent_id in self.agent_ids:
                start = self.grid.starts[agent_id]
                ids = []
                for i, goal in enumerate(self.grid.goals):
                    if start.color == goal.color:
                        ids.append(i)
                ids.sort(key=lambda x: self.grid.get_heuristic(Coord(start.x, start.y), x))
                goal_ids.append(ids)
            self.assigned_goals = filter(lambda x: len(x) == len(set(x)), itertools.product(*goal_ids))
            if enable_sorting:
                self.goal_pq = []

    def get_next_goal(self, maximum):
        """
        Gets the next set of goal assignments.
        Either from the iterator when sorting is disable or from the heap if it is enabled.
        :param maximum: The maximum cost used for pruning when sorting is enabled
        :return: The next goal assignment or None
        """
        if not self.enable_sorting:
            return next(self.assigned_goals, None)
        while len(self.goal_pq) < self.pq_size:
            next_push = next(self.assigned_goals, None)
            if next_push is None:
                break
            heuristic = self.get_initial_heuristic(next_push)
            if heuristic < maximum:
                heappush(self.goal_pq, Matching(next_push, heuristic))
        if len(self.goal_pq) == 0:
            return None
        next_goal = heappop(self.goal_pq)
        if next_goal.cost >= maximum:
            self.goal_pq = []
            return self.get_next_goal(maximum)
        else:
            return next_goal.goals

    def get_initial_heuristic(self, goals) -> int:
        """
        Calculate the initial heuristic for a specific goal assignment
        :param goals: The assigned goals
        :return: The heuristic
        """
        h = len(goals)
        assert len(self.agent_ids) == len(goals)
        for agent_id, index in zip(self.agent_ids, goals):
            start = self.grid.starts[agent_id]
            h += self.grid.get_heuristic(Coord(start.x, start.y), index)
        return h

    def solve(self, cat=None,upper_bound: Optional[int] = float("inf")) -> Optional[List[AgentPath]]:
        """
        Tries to solve the problem.
        :param cat: An optional Collision Avoidance table to use for all paths.
        :return: A list of paths for the given agents if a solution exists otherwise None
        """
        if self.heuristic_type == HeuristicType.Heuristic:
            return self.solve_matching(cat = cat, maximum = upper_bound)
        else:
            best = float("inf")
            best_solution = None
            goals = self.get_next_goal(best)
            while goals is not None:
                logger.log(f"Trying goal assignment of {goals} with maximum cost of {best}")
                solution = self.solve_matching(cat, best, dict(zip(self.agent_ids, goals)))
                if solution is not None:
                    cost = sum(map(lambda x: x.get_cost(), solution))
                    if cost < best:
                        best = cost
                        best_solution = solution
                goals = self.get_next_goal(best)
            return best_solution

    def solve_matching(self, cat: Optional[CAT], maximum=float("inf"), assigned_goals: dict = None) -> Optional[
        List[AgentPath]]:
        """
        Solves the problem with either an assigned matching or otherwise using a different heuristic.
        :param cat: The optional additional Collision Avoidance table to use.
        :param maximum: A maximum cost. Anything above this cost will be discarded.
        :param assigned_goals: A possible goal assignment when using exhaustive matching. Not needed when heuristic matching is used.
        :return: A list of paths if a solution exists, otherwise None
        """
        paths = PathSet(self.grid, self.agent_ids, self.heuristic_type, assigned_goals=assigned_goals)
        # Create list of used Collision Avoidance Tables
        cats = list()
        if cat is not None:
            cats.append(cat)
        cats.append(paths.cat)

        # Create initial agent paths
        # groups = Groups([Group(list(self.agent_ids))])
        groups = Groups([Group([n]) for n in self.agent_ids])
        for group in groups:
            problem = ODProblem(self.grid, group, cats, assigned_goals=assigned_goals)
            solver = ODSolver(problem, max_cost=paths.get_remaining_cost(group.agent_ids, maximum))
            group_paths = solver.solve()
            if group_paths is None:
                return None
            # Update the path and CAT table
            paths.update(group_paths)

        # Start looking for conflicts
        avoided_conflicts = set()
        conflict = paths.find_conflict()
        while conflict is not None:
            combine_groups = True
            a, b = conflict
            a_group = groups.group_map[a]
            b_group = groups.group_map[b]

            # Check if the conflict has been solved before. If so it has clearly failed
            combo = (a_group.agent_ids, b_group.agent_ids)
            if combo not in avoided_conflicts:
                avoided_conflicts.add(combo)

                # Try rerunning a while the b moves are not possible
                problem = ODProblem(self.grid, a_group, cats,
                                    illegal_moves=[paths[i] for i in b_group.agent_ids], assigned_goals=assigned_goals)

                # The maximum cost that it can have while still being optimal
                maximum_cost = paths[a].get_cost() + sum(paths[i].get_cost() for i in b_group.agent_ids)
                solver = ODSolver(problem, max_cost=maximum_cost)
                solution = solver.solve()
                if solution is not None:
                    # If a solution is found we can update the paths and we don't need to combine anything
                    combine_groups = False
                    paths.update(solution)
                else:
                    # Try redoing b by making a illegal
                    problem = ODProblem(self.grid, b_group, cats,
                                        illegal_moves=[paths[i] for i in a_group.agent_ids],
                                        assigned_goals=assigned_goals)

                    # The maximum cost that it can have while still being optimal
                    maximum_cost = paths[b].get_cost() + sum(paths[i].get_cost() for i in a_group.agent_ids)
                    solver = ODSolver(problem, max_cost=maximum_cost)
                    solution = solver.solve()
                    if solution is not None:
                        # If a solution is found we can update the paths and we don't need to combine anything
                        combine_groups = False
                        paths.update(solution)

            # Combine groups
            if combine_groups:
                group = groups.combine_agents(a, b)
                logger.log(f"Combining agents from groups of {a} and {b} into {group}")
                problem = ODProblem(self.grid, group, cats, assigned_goals=assigned_goals)
                solver = ODSolver(problem, max_cost=paths.get_remaining_cost(group.agent_ids, maximum))
                group_paths = solver.solve()
                if group_paths is None:
                    return None
                paths.update(group_paths)

            # Find next conflict
            conflict = paths.find_conflict()
        return paths.paths
