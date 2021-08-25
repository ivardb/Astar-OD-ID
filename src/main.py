import subprocess
from typing import Optional

from mapf_branch_and_bound.bbsolver import solve_bb
from mapfmclient import Problem, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from src.Astar_OD_ID.MatchingSolver import MatchingSolver
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

def solve_heur(starting_problem: Problem):
    problem = MatchingSolver(starting_problem, HeuristicType.Heuristic, enable_sorting=enable_sorting,
                             enable_matchingID=enable_id)
    solution = problem.solve(enable_cat=enable_cat)
    if solution is None:
        print("Failed to find solution")
        return None
    return solution

def solve_subroutine(starting_problem: Problem, upper_bound: Optional[int]):
    problem = MatchingSolver(starting_problem, heuristic_type = HeuristicType.Heuristic, enable_sorting=False,
                             enable_matchingID=False)
    if not upper_bound:
        upper_bound = float("inf")
    else:
        upper_bound += len(starting_problem.starts)
    solution = problem.solve(enable_cat=enable_cat,upper_bound=upper_bound)
    if solution is None:
        print("Failed to find solution")
        return None
    return solution

def solve_branch_and_bound(problem: Problem):
    return solve_bb(problem, solve_subroutine)


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
                                "A* + OD + ID with Hungarian heuristic", get_version(), debug, solver=solve_heur, cores=1)
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
        min_agents=1,
        max_agents=20,
        num_teams=2)
    descriptor = BenchmarkDescriptor(33,progressive_descriptor)
    debug = False
    version = "1.6.0"
    run_benchmark()
