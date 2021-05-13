import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker, BenchmarkDescriptor, ProgressiveDescriptor

from src.AstarID.IDProblem import IDProblem
from src.util.grid import HeuristicType
from src.util.map_generation.map_generation import generate_map
from src.util.visualization.visualizer import visualize


def solve(starting_problem: Problem) -> Solution:
    print()
    problem = IDProblem(starting_problem, heuristic_type)
    solution = problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    visualize(problem.grid, solution)
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
    benchmarker = MapfBenchmarker(api_token,
                                  BenchmarkDescriptor(1,
                                                      progressive_descriptor=ProgressiveDescriptor(
                                                          min_agents=20,
                                                          max_agents=20,
                                                          num_teams=10)
                                                      ),
                                  get_name(), get_version(), debug, solver=solve, cores=1)
    benchmarker.run()


def run_generated():
    problem = generate_map(20, 20, [2,1,1,1], max_neighbors=2, open_factor=0.5)
    solve(problem)


if __name__ == '__main__':
    version = "1.3.0"
    debug = True
    heuristic_type = HeuristicType.Exhaustive
    run_generated()
