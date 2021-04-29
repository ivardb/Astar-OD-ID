import subprocess

from mapfmclient import Problem, Solution, MapfBenchmarker

from src.AstarID.IDProblem import IDProblem


def solve(starting_problem: Problem) -> Solution:
    print()
    problem = IDProblem(starting_problem)
    solution = problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return solution


def get_version(debug, version) -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = "0.2.2"
    debug = True
    api_token = open("../apitoken.txt", "r").read().strip()
    benchmarker = MapfBenchmarker(api_token, 16, "A* + OD + ID", get_version(debug, version), debug, solver=solve, cores=1)
    benchmarker.run()
