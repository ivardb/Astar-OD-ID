import os
import re
from enum import Enum
from typing import List

import numpy
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


class DataTypes(Enum):
    Heuristic = 1
    ExhaustiveNoIdNoSort = 2
    ExhaustiveIdNoSort = 3
    ExhaustiveIdSort = 4

    def __str__(self):
        if self.value == 1:
            return "Heuristic"
        if self.value == 2:
            return "Exhaustive"
        if self.value == 3:
            return "Exhaustive + ID"
        return "Sorted Exhaustive + ID"


class StatTypes(Enum):
    Completion = 1
    Mean = 2
    Both = 3
    TeamMean = 4
    TeamCompletion = 5

    def __str__(self):
        if self.value == 1:
            return "C"
        if self.value == 2:
            return "M"
        if self.value == 3:
            return "B"
        if self.value == 4:
            return "TM"
        return "TC"


class ResultLoader:

    def __init__(self, result_root, name):
        self.result_root = result_root

        self.data = self.load_data(name)
        self.grouped_data = self.group_data()

        # Prefix, width, height, agents, teams, completed, mean, deviation
        self.aggregated_data = self.aggregate_data()

    def load_data(self, name):
        with open(os.path.join(self.result_root, name)) as f:
            data = []
            for line in f.readlines():
                split = line.split(",")
                folder = split[0].strip()
                name = split[1].strip()
                time = None if split[2].strip() == "None" else float(split[2].strip())
                data.append((folder, name, time))
            return data

    def group_data(self):
        grouped = dict()
        for folder, name, time in self.data:
            if folder not in grouped:
                grouped[folder] = list()
            grouped.get(folder).append(time)
        return grouped

    def aggregate_data(self):
        data = list()
        for key in self.grouped_data:
            value = self.grouped_data[key]
            matches: List[re.Match] = re.findall(f'^(\w+)-(\d+)x(\d+)-A(\d+)_T(\d+)$', key)
            completed = 0
            total = len(value)
            for val in value:
                if val is not None:
                    completed += 1
            filtered = list(filter(lambda x: x is not None, value))
            if len(filtered) > 0:
                mean = numpy.mean(filtered)
                deviation = numpy.std(filtered)
                completion = completed / total
            else:
                mean = float("nan")
                deviation = float("nan")
                completion = 0
            data.append((matches[0][0], int(matches[0][1]), int(matches[0][2]), int(matches[0][3]), int(matches[0][4]),
                         completion, mean, deviation))
        return data

    def filter(self, prefix=None, width=None, height=None, agents=None, max_agents=None, teams=None):
        data = self.aggregated_data
        if prefix is not None:
            data = filter(lambda x: x[0] == prefix, data)
        if width is not None:
            data = filter(lambda x: x[1] == width, data)
        if height is not None:
            data = filter(lambda x: x[2] == height, data)
        if agents is not None:
            data = filter(lambda x: x[3] == agents, data)
        if max_agents is not None:
            data = sorted(filter(lambda x: x[3] <= max_agents, data), key=lambda x: x[3])
        if teams is not None:
            data = filter(lambda x: x[4] == teams, data)
        return list(data)


def double_plot(data, types, teams, map_type):
    plt.rcParams["figure.figsize"] = (7, 5)
    plt.margins(0, 0)

    fig, (percentage, times) = plt.subplots(2, 1)
    plt.subplots_adjust(hspace=0.3)

    percentage.set_title(f"% solved out of 200 {map_type} maps")
    times.set_title(f"Average time needed for solved {map_type} maps")

    percentage.xaxis.set_major_locator(MaxNLocator(integer=True))
    percentage.set_ylabel("% solved")
    times.xaxis.set_major_locator(MaxNLocator(integer=True))

    times.set_xlabel(f'Number of agents spread over {teams} {"team" if teams == 1 else "teams"}')
    times.set_ylabel("seconds")
    percentage.set_ylim(0, 105)

    for d, t in zip(data, types):
        x = range(1, len(d) + 1)
        percentage.plot(x, list(map(lambda l: l[5] * 100, d)), label=f'{t}')
        times.plot(x, list(map(lambda l: l[6], d)), label=f'{t}')
    plt.legend()
    return plt


def team_double_plot(data1, data3, types, map_type, stat_type):
    plt.rcParams["figure.figsize"] = (7, 5)
    plt.margins(0, 0)

    fig, (team1, team3) = plt.subplots(2, 1)
    plt.subplots_adjust(hspace=0.3)

    if stat_type == StatTypes.TeamMean:
        team1.set_title(f"Average time needed for solved {map_type} maps (1 team)")
        team3.set_title(f"Average time needed for solved {map_type} maps (3 teams)")

        team1.xaxis.set_major_locator(MaxNLocator(integer=True))
        team1.set_ylabel("seconds")
        team3.xaxis.set_major_locator(MaxNLocator(integer=True))

        team3.set_xlabel(f'Number of agents')
        team3.set_ylabel("seconds")

        for (d1, d3), t in zip(zip(data1, data3), types):
            team1.plot(range(1, len(d1) + 1), list(map(lambda l: l[6], d1)), label=f'{t}')
            team3.plot(range(1, len(d3) + 1), list(map(lambda l: l[6], d3)), label=f'{t}')
    else:
        team1.set_title(f"% solved out of 200 {map_type} maps (1 team)")
        team3.set_title(f"% solved out of 200 {map_type} maps (3 teams)")

        team1.xaxis.set_major_locator(MaxNLocator(integer=True))
        team1.set_ylabel("% solved")
        team1.set_ylim(0, 105)
        team3.xaxis.set_major_locator(MaxNLocator(integer=True))

        team3.set_xlabel(f'Number of agents')
        team3.set_ylabel("% solved")
        team3.set_ylim(0, 105)

        for (d1, d3), t in zip(zip(data1, data3), types):
            team1.plot(range(1, len(d1) + 1), list(map(lambda l: l[5] * 100, d1)), label=f'{t}')
            team3.plot(range(1, len(d3) + 1), list(map(lambda l: l[5] * 100, d3)), label=f'{t}')
    plt.legend()
    return plt


def comparison_plot(data, types, teams, map_type, stat_type):
    #plt.style.use('seaborn-whitegrid')
    if stat_type == StatTypes.Both:
        return double_plot(data, types, teams, map_type)
    x = range(1, len(data[0]) + 1)
    fig, ax1 = plt.subplots()
    plt.xticks(list(range(1, len(data[0]) + 1)))
    ax1.set_xlabel(f'Number of agents spread over {teams} {"team" if teams == 1 else "teams"}')
    if stat_type == StatTypes.Completion:
        plt.ylim([0, 101])
        ax1.set_ylabel('% of problems solved within 2 minutes')
        for d, t in zip(data, types):
            ax1.plot(x, list(map(lambda d: d[5] * 100, d)), label=f'{t}')
        ax1.legend(loc=(0, 0.4))
        #plt.title(f'Completion % within 2 minutes for {map_type} maps', font)

    elif stat_type == StatTypes.Mean:
        ax1.set_ylabel('Average time in seconds')
        for d, t in zip(data, types):
            ax1.plot(x, list(map(lambda d: d[6], d)), label=f'{t}')
        ax1.legend(loc=(0, 0.4))
        #plt.title(f'Average runtime for solved {map_type} maps', font)
    return plt


def save_plot(plt, name):
    image_folder = "C:\\Users\\ivard\\Documents\\Uni\\CSE-3\\CSE3000 - Research Project\\Docs\\Research paper\\images"
    path = os.path.join(image_folder, name)
    plt.savefig(path, bbox_inches='tight', pad_inches=0.1)


def compare(teams, agents, prefix, plot_type, save, *types):
    loaders = [get_loader(type) for type in types]
    data = [loader.filter(prefix=prefix, teams=teams, max_agents=agents) for loader in loaders]
    plt = comparison_plot(data, types, teams, prefix, plot_type)
    if save:
        alg_name = ''.join(map(str, sorted(map(lambda l: l.value, types))))
        image_name = f"{alg_name}-{plot_type}-{prefix}{teams}.png"
        save_plot(plt, image_name)
    plt.show()


def team_compare(agents1, agents3, prefix, plot_type, save, *types):
    loaders = [get_loader(type) for type in types]
    data1 = [loader.filter(prefix=prefix, teams=1, max_agents=agents1) for loader in loaders]
    data3 = [loader.filter(prefix=prefix, teams=3, max_agents=agents3) for loader in loaders]
    plt = team_double_plot(data1, data3, types, prefix, plot_type)
    if save:
        alg_name = ''.join(map(str, sorted(map(lambda l: l.value, types))))
        image_name = f"{alg_name}-{plot_type}-{prefix}.png"
        save_plot(plt, image_name)
    plt.show()


def plot_progressive(save, *types):
    loaders = [get_loader(type) for type in types]
    data = [loader.filter(prefix="Progressive") for loader in loaders]

    x = range(1, len(data[0]) + 1)
    fig, ax1 = plt.subplots()
    plt.xticks(list(range(1, len(data[0]) + 1)))
    ax1.set_ylabel('Average time in seconds')
    ax1.set_xlabel("Number of teams")
    for d, t in zip(data, types):
        ax1.plot(x, list(map(lambda l: l[6], sorted(d, key=lambda l: l[4]))), label=f'{t}')
    ax1.legend(loc=(0, 0.4))
    if save:
        alg_name = ''.join(map(str, sorted(map(lambda l: l.value, types))))
        image_name = f"{alg_name}-M-Progressive.png"
        save_plot(plt, image_name)
    plt.show()


def get_loader(plot_type):
    if plot_type == DataTypes.Heuristic:
        return ResultLoader("../../../results", "H.txt")
    elif plot_type == DataTypes.ExhaustiveNoIdNoSort:
        return ResultLoader("../../../results", "E-NoId-NoSort.txt")
    elif plot_type == DataTypes.ExhaustiveIdNoSort:
        return ResultLoader("../../../results", "E-Id-NoSort.txt")
    return ResultLoader("../../../results", "E-Id-Sort.txt")


if __name__ == '__main__':
    #compare(3, 13, "Obstacle", StatTypes.Both, False, DataTypes.ExhaustiveNoIdNoSort, DataTypes.ExhaustiveIdNoSort)
    #team_compare(8, 13, "Maze", StatTypes.TeamMean, False, DataTypes.ExhaustiveNoIdNoSort, DataTypes.ExhaustiveIdNoSort)
    plot_progressive(False, DataTypes.ExhaustiveNoIdNoSort, DataTypes.ExhaustiveIdNoSort, DataTypes.ExhaustiveIdSort)
