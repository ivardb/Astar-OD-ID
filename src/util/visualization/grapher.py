import os
import re
from typing import List

from matplotlib import pyplot as plt


class ResultLoader:

    def __init__(self, result_root, name):
        self.result_root = result_root
        # Prefix, width, height, agents, teams, completed, mean, deviation
        self.data = self.load_data(name)

    def load_data(self, name):
        with open(os.path.join(self.result_root, name)) as f:
            data = []
            for line in f.readlines():
                matches: List[re.Match] = re.findall(f'^(\w+)-(\d+)x(\d+)-A(\d+)_T(\d+): \w+: (\d+.\d+|nan), [\w ]+: (\d+.\d+|nan), [\w ]+: (\d+.\d+|nan)$', line)
                data.append((matches[0][0],
                             int(matches[0][1]),
                             int(matches[0][2]),
                             int(matches[0][3]),
                             int(matches[0][4]),
                             float(matches[0][5]),
                             float(matches[0][6]),
                             float(matches[0][7]))
                            )
            return data

    def filter(self, prefix=None, width=None, height=None, agents=None, teams=None):
        data = self.data
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


def split_teams(data, parameter, num_agents):
    res = ([float('nan')] * num_agents, [float('nan')] * num_agents)
    for row in data:
        if row[3] > num_agents:
            continue
        if row[4] == 1:
            res[0][row[3] - 1] = row[parameter]
        elif row[4] == 3:
            res[1][row[3] - 1] = row[parameter]
    return res


def line_plot(data, num_agents, matching_type, maze_type, plot_type='completed'):

    font = {'fontname': 'Consolas'}
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('#D9D9D9')

    if plot_type == 'completed':
        t1, t3 = split_teams(data, 5, num_agents)
        t11, t31 = split_teams(data, 6, num_agents)
        x = range(1, num_agents + 1)

        print(f"x: {len(x)}\nt1: {len(t1)}\nt3: {len(t3)}")

        ax1.set_xlabel('Number of agents')
        ax1.set_ylabel('Fraction of problems solved within 30 seconds')
        ax1.plot(x, t1, label=f'amount solved (1 team)', color='#0000ff', linestyle='--')
        ax1.plot(x, t3, label=f'amount solved (3 teams)', color='#ff0000', linestyle='--')
        ax1.legend(loc=(0,0.4))

        ax2 = ax1.twinx()
        plt.ylim([0, 30])
        ax2.set_ylabel('Average runtime (s)')
        ax2.plot(x, t11, label=f'average runtime (1 team)', color='#5555ff')
        ax2.plot(x, t31, label=f'average runtime (3 teams)', color='#ff5555')
        ax2.legend(loc=(0,0.6))


    plt.title(f'{matching_type} matching performance for {maze_type} maps', font)

    plt.show()


if __name__ == '__main__':
    result_loader = ResultLoader("../../../results", "Heuristic.txt")
    for prefix in ["Open"]:
        plot_data = result_loader.filter(prefix=prefix)
        line_plot(plot_data, 15, "Heuristic", prefix)
