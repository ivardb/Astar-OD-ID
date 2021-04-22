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

    def __init__(self, problem: mapfmclient.Problem):
        self.grid = Grid(problem.grid, problem.width, problem.height, problem.starts,
                         problem.goals, compute_heuristics=True)
        self.initial = MapfmState(map(lambda i: (i.x, i.y), self.grid.starts))

    def expand(self, parent: MapfmState) -> Iterable[Tuple[State, int]]:
        moves: List[List[Tuple[Coord, int, int]]] = []
        for coord, acc in zip(parent.coords, parent.accumulated_cost):
            agent_moves = []
            for moved in self.grid.get_neighbors(coord):
                agent_moves.append((moved, 0, acc + 1))
            agent_moves.append((coord, acc + 1, 0))
            moves.append(agent_moves)
        states = itertools.product(*moves)
        proper_states = []
        for state in states:
            cost = 0
            coords = []
            accumulators = []
            for coord, acc, c in state:
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
        h = 0
        for i, coord in enumerate(state.coords):
            h += self.grid.get_heuristic(coord, i)
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
        for j in range(i, len(old.coords)):
            if old.coords[i] == new.coords[j] and old.coords[j] == new.coords[i]:
                return False
    return True
