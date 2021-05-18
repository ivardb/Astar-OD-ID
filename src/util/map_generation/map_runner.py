from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from src.AstarID.MatchingID import MatchingID
from src.util.grid import HeuristicType
from src.util.map_generation.map_parser import MapParser


class BenchmarkQueue:

    def __init__(self, name):
        self.name = name
        with open(name, 'a'):
            pass

    def get_next(self):
        with open(self.name, 'r') as f:
            return f.readline().strip()

    def completed(self):
        with open(self.name, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(self.name, 'w') as fout:
            fout.writelines(data[1:])

    def add(self, data):
        with open(self.name, 'a') as f:
            f.write(data + "\n")


class MapRunner:

    def __init__(self, map_root, heuristic_type):
        self.map_root = map_root
        self.heuristic_type = heuristic_type
        self.map_parser = MapParser(map_root)

    def timeout(self, current_problem: Problem, time) -> Optional[Solution]:
        try:
            sol = func_timeout(time, self.solve, args=(current_problem,))

        except FunctionTimedOut:
            sol = None
        except Exception as e:
            print(f"An error occurred while running: {e}")
            return None
        return sol

    def solve(self, starting_problem: Problem) -> Solution:
        problem = MatchingID(starting_problem, self.heuristic_type)
        solution = problem.solve()
        if solution is None:
            print("Failed to find solution")
            return None
        return solution

    def test_generated(self, time, folder):
        problems = self.map_parser.parse_batch(folder)
        solved = 0
        run = 0

        for i, problem in enumerate(problems):
            print(f"Testing: {folder} Run: {i + 1}/{len(problems)}, Solved: {solved}/{run}", end='   ')
            solution = self.timeout(problem, time)
            run += 1
            if solution is not None:
                print("Solved")
                solved += 1
            else:
                print("Failed")
        return solved/run

    def test_queue(self, time, queue: BenchmarkQueue, output):
        task = queue.get_next()
        while task is not None and task != "":
            with open(output, 'a') as f:
                res = self.test_generated(time, task)
                f.write(f"{task}: {res}\n")
                print(f"{task}: {res}\n")
                queue.completed()
                task = queue.get_next()


if __name__ == "__main__":
    map_root = "../../../maps"
    queue = BenchmarkQueue("queue.txt")
    runner = MapRunner(map_root, HeuristicType.Exhaustive)
    runner.test_queue(10, queue, "results.txt")
