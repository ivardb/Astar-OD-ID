import os
from multiprocessing import Pool
from typing import Optional

import time
from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from Astar_OD_ID.MatchingSolver import MatchingSolver
from benchmarking.map_parser import MapParser
from src.util.grid import HeuristicType


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


class Dummy:

    def __init__(self, timeout, heuristic_type, enable_id, enable_sorting):
        self.timeout = timeout
        self.heuristic_type = heuristic_type
        self.enable_id = enable_id
        self.enable_sorting = enable_sorting

    def __call__(self, object):
        return object[0], test(object[1], self.timeout, self.heuristic_type, self.enable_id, self.enable_sorting)


class MapRunner:

    def __init__(self, map_root, heuristic_type):
        self.map_root = map_root
        self.heuristic_type = heuristic_type
        self.map_parser = MapParser(map_root)

    def test_queue(self, timeout, queue: BenchmarkQueue, output):
        task = queue.get_next()
        while task is not None and task != "":
            print(task)
            res = self.test_generated(timeout, task)
            with open(output, 'a') as f:
                for r in res:
                    f.write(f"{task}, {r[0]}, {r[1]}\n")
                queue.completed()
                task = queue.get_next()

    def test_generated(self, timeout, folder):
        problems = self.map_parser.parse_batch(folder)

        with Pool(processes=processes) as p:
            res = p.map(Dummy(timeout, self.heuristic_type, enable_id, enable_sorting), problems)
        print()
        return res


def test(problem: Problem, time_out, heuristic_type, enable_id, enable_sorting):
    start_time = time.process_time()
    solution = timeout(problem, time_out, heuristic_type, enable_id, enable_sorting)
    print('.', end='', flush=True)
    if solution is not None:
        return time.process_time() - start_time
    else:
        return None


def timeout(current_problem: Problem, time_out, heuristic_type, enable_id, enable_sorting) -> Optional[Solution]:
    try:
        sol = func_timeout(time_out, solve, args=(current_problem, heuristic_type, enable_id, enable_sorting))

    except FunctionTimedOut:
        sol = None
    except Exception as e:
        return None
    return sol


def solve(starting_problem: Problem, heuristic_type, enable_id, enable_sorting):
    print()
    problem = MatchingSolver(starting_problem, heuristic_type, enable_sorting=enable_sorting,
                             enable_matchingID=enable_id)
    solution = problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return solution


if __name__ == "__main__":
    enable_id = True
    enable_sorting = True
    processes = 10
    map_root = "../../maps/progressive"
    result_root = "../../results"
    queue = BenchmarkQueue("queue.txt")
    runner = MapRunner(map_root, HeuristicType.Exhaustive)
    runner.test_queue(120, queue, os.path.join(result_root, "test.txt"))
