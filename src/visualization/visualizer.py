from copy import deepcopy

import matplotlib
from mapfmclient import Solution
from matplotlib import pyplot as plt

from src.util.grid import Grid

matplotlib.use("TkAgg")


def visualize(grid: Grid, solution: Solution):
    max_t = max(map(lambda x: len(x.route), solution.paths))
    base = grid.grid

    for goal in grid.goals:
        base[goal.y][goal.x] = goal.color + 2
    for t in range(max_t):
        plt.figure(1)
        plt.clf()
        image = deepcopy(base)
        for i, path in enumerate(solution.paths):
            if t < len(path.route):
                x, y = path.route[t]
            else:
                x, y = path.route[-1]
            image[y][x] = grid.starts[i].color + 2
        plt.imshow(image)
        plt.pause(.3)
