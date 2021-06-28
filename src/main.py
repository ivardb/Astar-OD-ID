import subprocess

from mapfmclient import Problem, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from Astar_OD_ID.MatchingSolver import MatchingSolver
from src.util.grid import HeuristicType
from src.util.logger.logger import Logger


def solve(starting_problem: Problem):
    print()
    problem = MatchingSolver(starting_problem, heuristic_type, enable_sorting=enable_sorting,
                             enable_matchingID=enable_id)
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
        return f"A* + OD + ID with exhaustive matching ({int(enable_cat)}{int(enable_id)}{int(enable_sorting)})"
    else:
        return f"A* + OD + ID with heuristic matching ({int(enable_cat)}{int(enable_id)}{int(enable_sorting)})"


def run_benchmark():
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmark = MapfBenchmarker(api_token, descriptor,
                                get_name(), get_version(), debug, solver=solve, cores=1)
    benchmark.run()


def activate_logging():
    loggers = []
    if logMatching:
        loggers.append("MatchingSolver")
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

    # Configure algorithm
    heuristic_type = HeuristicType.Exhaustive
    enable_cat = True
    enable_id = True
    enable_sorting = False

    # Configure benchmark
    progressive_descriptor = ProgressiveDescriptor(
        min_agents=20,
        max_agents=20,
        num_teams=10)
    descriptor = BenchmarkDescriptor(16)
    debug = True
    version = "1.6.0"
    run_benchmark()
