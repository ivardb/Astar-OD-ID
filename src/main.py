from typing import List, Optional

from mapfmclient import Problem, Solution, MapfBenchmarker

from src.Astar.MAPFMproblem import MapfmProblem, MapfmState
from src.Astar.solver import Solver


def solve(problem: Problem) -> Solution:
    solver = Solver(MapfmProblem(problem))
    solution: Optional[List[MapfmState]] = solver.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    paths = [[] for _ in solution[0].coords]
    for path in solution:
        for index, coord in enumerate(path.coords):
            paths[index].append((coord.x, coord.y))
    return Solution.from_paths(paths)


if __name__ == '__main__':
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmarker = MapfBenchmarker(api_token, 10, "A*", "0.0.1", True, solver=solve, cores=1)
    benchmarker.run()
