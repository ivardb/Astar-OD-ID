import subprocess
from typing import List, Optional

from mapfmclient import Problem, Solution, MapfBenchmarker

from src.Astar.MAPFMproblem import MapfmProblem
from src.Astar.MAPFMstate import MapfmState
from src.Astar.solver import Solver


def solve(problem: Problem) -> Solution:
    solver = Solver(MapfmProblem(problem))
    solution: Optional[List[MapfmState]] = solver.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    paths = [[] for _ in solution[0].agents]
    for path in solution:
        for index, agent in enumerate(path.agents):
            paths[index].append((agent.coords.x, agent.coords.y))
    return Solution.from_paths(paths)


def get_version(debug, version) -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = "0.1.2"
    debug = True
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmarker = MapfBenchmarker(api_token, 1, "A* + OD", get_version(debug, version), debug, solver=solve, cores=1)
    benchmarker.run()
