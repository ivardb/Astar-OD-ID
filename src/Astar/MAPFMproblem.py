import itertools
from typing import Tuple, Iterable, List, Optional

import mapfmclient

from src.Astar.problem import AStarProblem, State
from src.util.grid import Grid
from src.util.coord import Coord


class MapfmState(State):
    def __init__(self, coords: Iterable[Tuple[int, int]], accumulated_cost: Optional[List[int]] = None):
        self.coords = tuple((Coord(*i) for i in coords))
        self.accumulated_cost: Tuple[int] = tuple(0 for _ in self.coords) if accumulated_cost is None else tuple(
            accumulated_cost)

    def __hash__(self) -> int:
        return tuple.__hash__((self.coords, self.accumulated_cost))

    def __eq__(self, other):
        return self.coords == other.coords and self.accumulated_cost == other.accumulated_cost


class MapfmProblem(AStarProblem):

    def __init__(self, problem: mapfmclient.Problem, precompute_matching=False):
        self.precompute = precompute_matching
        proper_start = problem.starts
        proper_goals = problem.goals
        if self.precompute:
            new_goals = []
            for start in proper_start:
                for goal in proper_goals:
                    if start.color == goal.color:
                        new_goals.append(goal)
                        proper_goals.remove(goal)
                        break
            proper_goals = new_goals

        self.grid = Grid(problem.grid, problem.width, problem.height, proper_start, proper_goals, compute_heuristics=True)
        self.initial = MapfmState(map(lambda i: (i.x, i.y), self.grid.starts))

    def expand(self, parent: MapfmState) -> Iterable[Tuple[State, int]]:
        moves: List[List[Tuple[Coord, int, int]]] = []
        for i, (coord, acc) in enumerate(zip(parent.coords, parent.accumulated_cost)):
            agent_moves = []
            for moved in self.grid.get_neighbors(coord):
                agent_moves.append((moved, 0, acc + 1))
            if self.grid.get_heuristic(coord, i) == 0:
                agent_moves.append((coord, acc + 1, 0))
            else:
                agent_moves.append((coord, 0, 1))
            moves.append(agent_moves)
        states = itertools.product(*moves)
        proper_states = []
        for state in states:
            cost = 0
            coords = []
            accumulators = []
            for coord, acc, c in state:
                #TODO: Improve vertex conflict checking by putting it here
                coords.append(coord)
                accumulators.append(acc)
                cost += c
            proper_state = MapfmState(coords, accumulators)
            if valid_state(parent, proper_state):
                proper_states.append((proper_state, cost))
        return proper_states

    def initial_state(self) -> MapfmState:
        return self.initial

    def is_final(self, state: MapfmState) -> bool:
        return self.grid.is_final(state.coords)

    def heuristic(self, state: MapfmState) -> int:
        if self.precompute:
            return self.heuristicMatched(state)
        return self.heuristicColor(state)

    def heuristicMatched(self, state: MapfmState) -> int:
        h = 0
        for i, coord in enumerate(state.coords):
            h += self.grid.get_heuristic(coord, i)
        return h

    def heuristicColor(self, state: MapfmState) -> int:
        h = 0
        for i, coord in enumerate(state.coords):
            min_dist = float('inf')
            for j, goal in enumerate(self.grid.goals):
                if self.grid.starts[i].color == goal.color:
                    if self.grid.get_heuristic(coord, j) < min_dist:
                        min_dist = self.grid.get_heuristic(coord, j)
            h += min_dist
        return h


def valid_state(old: MapfmState, new: MapfmState) -> bool:
    # Check for vertex conflicts:
    vertex_set = set()
    for coord in new.coords:
        if coord in vertex_set:
            return False
        vertex_set.add(coord)
    # Check for edge conflicts, which will all be swapping conflicts in a grid
    for i in range(len(old.coords)):
        for j in range(i+1, len(old.coords)):
            if old.coords[i] == new.coords[j] and old.coords[j] == new.coords[i]:
                return False
    return True

