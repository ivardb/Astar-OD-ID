import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from src.AstarID.MatchingID import MatchingID
from src.util.grid import HeuristicType
from src.util.logger.logger import Logger


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


def run_benchmark():
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmark = MapfBenchmarker(api_token, descriptor,
                                  get_name(), get_version(), debug, solver=solve, cores=1)
    benchmark.run()


def activate_logging():
    loggers = []
    if logMatching:
        loggers.append("MatchingID")
    if logID:
        loggers.append("IDProblem")
    if logSolver:
        loggers.append("Solver")
    Logger.activate_loggers(*loggers)
    Logger.activate()


if __name__ == '__main__':
    # Configure logging
    logMatching = True
    logID = True
    logSolver = True
    activate_logging()

    heuristic_type = HeuristicType.Exhaustive
    enable_cat = True
    progressive_descriptor = ProgressiveDescriptor(
        min_agents=20,
        max_agents=20,
        num_teams=10)
    descriptor = BenchmarkDescriptor(14)
    debug = True
    version = "1.4.0"
    run_benchmark()
