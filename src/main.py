from mapfmclient import Problem, Solution, MarkedLocation, MapfBenchmarker

from src.grid import Grid


def solve(problem: Problem) -> Solution:
    grid = Grid(problem.grid, problem.width, problem.height, problem.starts, problem.goals, compute_heuristics=True)
    return Solution.from_paths([])


if __name__ == '__main__':
    api_token = open("apitoken.txt", "r").read().strip()
    benchmarker = MapfBenchmarker(api_token, 3, "A*+ID+OD", "v0.1", True, solver=solve, cores=1)
    benchmarker.run()
