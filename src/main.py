import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker

from src.AstarID.IDProblem import IDProblem
from src.util.grid import HeuristicType


def solve(starting_problem: Problem) -> Solution:
    print()
    problem = IDProblem(starting_problem, heuristic_type)
    solution = problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return solution


def get_version() -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


def get_name() -> str:
    if heuristic_type == HeuristicType.Exhaustive:
        return "A* + OD + ID with exhaustive matching"
    else:
        return "A* + OD + ID with heuristic matching"


if __name__ == '__main__':
    version = "1.3.0"
    debug = True
    heuristic_type = HeuristicType.Color
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmarker = MapfBenchmarker(api_token, 14, get_name(), get_version(), debug, solver=solve, cores=1)
    benchmarker.run()
