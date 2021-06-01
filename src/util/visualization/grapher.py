import os
import re
from enum import Enum
from typing import List

import numpy
from matplotlib import pyplot as plt


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
            mean = numpy.mean(filtered)
            deviation = numpy.std(filtered)
            data.append((matches[0][0], int(matches[0][1]), int(matches[0][2]), int(matches[0][3]), int(matches[0][4]),
                         completed / total, mean, deviation))
        return data

    def filter(self, prefix=None, width=None, height=None, agents=None, teams=None):
        data = self.aggregated_data
        if prefix is not None:
            data = filter(lambda x: x[0] == prefix, data)
        if width is not None:
            data = filter(lambda x: x[1] == width, data)
        if height is not None:
            data = filter(lambda x: x[2] == height, data)
        if agents is not None:
            data = filter(lambda x: x[3] == agents, data)
        if teams is not None:
            data = filter(lambda x: x[4] == teams, data)
        return list(data)


def comparison_plot(data1, data2, matching_type1, matching_type2, teams, num_agents, map_type, stat_type):
    font = {'fontname': 'Consolas'}
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('#D9D9D9')

    x = range(1, num_agents + 1)
    ax1.set_xlabel(f'Number of agents spread over {teams} {"team" if teams == 1 else "teams"}')
    if stat_type == StatTypes.Completion:
        plt.ylim([0, 1.01])
        ax1.set_ylabel('Fraction of problems solved within 30 seconds')
        ax1.plot(x, list(map(lambda d: d[5], data1)), label=f'{matching_type1}', color='#0000ff', linestyle='--')
        ax1.plot(x, list(map(lambda d: d[5], data2)), label=f'{matching_type2}', color='#ff0000', linestyle='--')
        ax1.legend(loc=(0, 0.4))

    elif stat_type == StatTypes.Mean:
        ax1.set_ylabel('Average time needed to solve problems')
        ax1.plot(x, list(map(lambda d: d[6], data1)), label=f'{matching_type1}', color='#0000ff', linestyle='--')
        ax1.plot(x, list(map(lambda d: d[6], data2)), label=f'{matching_type2}', color='#ff0000', linestyle='--')
        ax1.legend(loc=(0, 0.4))

    plt.title(f'{matching_type1} versus {matching_type2} for {map_type} maps', font)

    plt.show()


def compare(type1, type2, teams, agents, prefix, plot_type):
    loader1 = get_loader(type1)
    loader2 = get_loader(type2)
    data1 = loader1.filter(prefix=prefix, teams=teams)
    data2 = loader2.filter(prefix=prefix, teams=teams)
    comparison_plot(data1, data2, type1, type2, teams, agents, prefix, plot_type)


def get_loader(plot_type):
    if plot_type == DataTypes.Heuristic:
        return ResultLoader("../../../results", "H.txt")
    elif plot_type == DataTypes.ExhaustiveNoIdNoSort:
        return ResultLoader("../../../results", "E-NoId-NoSort.txt")
    elif plot_type == DataTypes.ExhaustiveIdNoSort:
        return ResultLoader("../../../results", "E-Id-NoSort.txt")
    return ResultLoader("../../../results", "E-Id-Sort.txt")


if __name__ == '__main__':
    compare(DataTypes.ExhaustiveIdSort, DataTypes.ExhaustiveNoIdNoSort, 3, 8, "Obstacle", StatTypes.Mean)
