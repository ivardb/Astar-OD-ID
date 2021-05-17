import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from src.AstarID.MatchingID import MatchingID
from src.util.grid import HeuristicType


def solve(starting_problem: Problem) -> Solution:
    print()
    problem = MatchingID(starting_problem, heuristic_type)
    solution = problem.solve(enable_cat=enable_cat)
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
    version = "1.4.0"
    debug = True
    heuristic_type = HeuristicType.Exhaustive
    enable_cat = False # TODO: Test if worth it or not
    api_token = open("../apitoken.txt", "r").read().strip()
    progressive_descriptor = ProgressiveDescriptor(
        min_agents=20,
        max_agents=20,
        num_teams=10)
    benchmarker = MapfBenchmarker(api_token, BenchmarkDescriptor(1, progressive_descriptor),
                                  get_name(), get_version(), debug, solver=solve, cores=1)
    benchmarker.run()
