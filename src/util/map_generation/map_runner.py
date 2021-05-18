from multiprocessing import Pool
from typing import Optional

import time
from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from src.AstarID.IDProblem import IDProblem
from src.AstarID.MatchingID import MatchingID
from src.util.AgentPath import AgentPath
from src.util.grid import HeuristicType, Grid
from src.util.group import Group
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


class Dummy:

    def __init__(self, timeout, heuristic_type):
        self.timeout = timeout
        self.heuristic_type = heuristic_type

    def __call__(self, object):
        return test(object, self.timeout, self.heuristic_type)


class MapRunner:

    def __init__(self, map_root, heuristic_type):
        self.map_root = map_root
        self.heuristic_type = heuristic_type
        self.map_parser = MapParser(map_root)

    def test_queue(self, timeout, queue: BenchmarkQueue, output):
        task = queue.get_next()
        while task is not None and task != "":
            with open(output, 'a') as f:
                res, duration = self.test_generated(timeout, task)
                f.write(f"{task}: Completed: {res}, Average Time: {duration}s\n")
                print(f"{task}: {res} with average {duration}s\n")
                queue.completed()
                task = queue.get_next()

    def test_generated(self, timeout, folder):
        problems = self.map_parser.parse_batch(folder)

        with Pool(processes=4) as p:
            res = p.map(Dummy(timeout, self.heuristic_type), problems)
        print()

        solved = 0
        times = []
        for s, t in res:
            solved += s
            times.append(t)
        total = 0
        count = 0
        for duration in times:
            if duration is not None:
                total += duration
                count += 1
        return solved/len(problems), round(total/count, 3)


def test(problem: Problem, time_out, heuristic_type):
    start_time = time.process_time()
    solution = timeout(problem, time_out, heuristic_type)
    print('.', end='')
    if solution is not None:
        return 1, (time.process_time() - start_time)
    else:
        return 0, None


def timeout(current_problem: Problem, time_out, heuristic_type) -> Optional[Solution]:
    try:
        sol = func_timeout(time_out, solve_no_id, args=(current_problem, heuristic_type))

    except FunctionTimedOut:
        sol = None
    except Exception as e:
        print(f"An error occurred while running: {e}")
        return None
    return sol


def solve(starting_problem: Problem, heuristic_type):
    problem = MatchingID(starting_problem, heuristic_type)
    solution = problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return solution


def solve_no_id(starting_problem: Problem, heuristic_type):
    grid = Grid(starting_problem.grid, starting_problem.width, starting_problem.height, starting_problem.starts, starting_problem.goals, heuristic_type)
    id_problem = IDProblem(grid, heuristic_type, Group(range(len(starting_problem.starts))))
    solution = id_problem.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return AgentPath.to_solution(solution)


if __name__ == "__main__":
    map_root = "../../../maps"
    queue = BenchmarkQueue("queue.txt")
    runner = MapRunner(map_root, HeuristicType.Exhaustive)
    runner.test_queue(30, queue, "MatchingIDComparison.txt")
