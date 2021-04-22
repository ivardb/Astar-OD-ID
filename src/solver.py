from abc import ABC, abstractmethod
from heapq import heappush, heappop
from typing import List, Optional, Hashable, Iterable, Tuple


class Node:

    def __init__(self, state, cost, heuristic, parent=None):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


class State(ABC, Hashable):
    @abstractmethod
    def __eq__(self, other):
        pass

    def next(self, parent):
        """
        Optional next method. Called once on every child when it is made with it's parent.
        :param parent: parent state
        :return: nothing
        """
        return


class AStarProblem(ABC):

    @abstractmethod
    def expand(self, parent: State) -> Iterable[Tuple[State, int]]:
        """
        :param parent:
        :return: a list of tuples containing the next state,
                 and the cost of going to that state.
        """
        raise NotImplemented

    @abstractmethod
    def initial_state(self) -> State:
        raise NotImplemented

    @abstractmethod
    def is_final(self, state: State) -> bool:
        raise NotImplemented

    @abstractmethod
    def heuristic(self, state: State) -> int:
        raise NotImplemented


def path(node: Node) -> List[State]:
    curr = node
    path = []
    while curr is not None:
        path.insert(0, curr.state)
        curr = curr.parent
    return path


class Solver:

    def __init__(self, problem: AStarProblem):
        self.problem = problem

    def solve(self) -> Optional[List[State]]:
        initial_state = self.problem.initial_state()
        initial_heuristic = self.problem.heuristic(initial_state)

        expanded = set()
        frontier: List[Node] = []
        heappush(frontier, Node(initial_state, 0, initial_heuristic))

        while frontier:
            current = heappop(frontier)
            if current in expanded:
                continue
            if self.problem.is_final(current.state):
                return path(current)

            expanded.add(current)
            states = self.problem.expand(current.state)
            for state, cost_increase in states:
                if state not in expanded:
                    heappush(frontier, Node(state, current.cost + cost_increase, self.problem.heuristic(state), current))
        return None
