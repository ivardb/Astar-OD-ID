import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from src.AstarID.IDProblem import IDProblem
from src.AstarID.MatchingID import MatchingID
from src.util.AgentPath import AgentPath
from src.util.grid import HeuristicType, Grid
from src.util.group import Group
from src.util.logger.logger import Logger


def solve_with_id(starting_problem: Problem) -> Solution:
    print()
    problem = MatchingID(starting_problem, heuristic_type, enable_sorting=enable_sorting)
    solution = problem.solve(enable_cat=enable_cat)
    if solution is None:
        print("Failed to find solution")
        return None
    return solution


def solve_no_id(starting_problem: Problem):
    grid = Grid(starting_problem.grid, starting_problem.width, starting_problem.height, starting_problem.starts, starting_problem.goals, heuristic_type)
    id_problem = IDProblem(grid, heuristic_type, Group(range(len(starting_problem.starts))), enable_sorting=enable_sorting)
    solution = id_problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return AgentPath.to_solution(solution)


def solve(starting_problem: Problem):
    if enable_id:
        return solve_with_id(starting_problem)
    else:
        return solve_no_id(starting_problem)


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
