from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Hashable


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
