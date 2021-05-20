from src.util.group import Group


class Groups:

    def __init__(self, groups):
        """
        Create a set of groups.
        :param groups: The groups
        """
        self.groups = groups
        self.group_map = dict()
        for group in groups:
            for agent in group.agent_ids:
                self.group_map[agent] = group

    def __iter__(self):
        return self.groups.__iter__()

    def __next__(self):
        return self.groups.__next__()

    def combine_agents(self, a, b) -> Group:
        """
        Combine the groups to which the agents belong.
        :param a: An agent to combine
        :param b: An agent to combine
        :return: The new combined group
        """
        group_a = self.group_map[a]
        group_b = self.group_map[b]
        group = group_a.combine(group_b)
        self.groups.remove(group_a)
        self.groups.remove(group_b)
        self.groups.append(group)
        for agent in group.agent_ids:
            self.group_map[agent] = group
        return group
