from __future__ import annotations

from typing import Iterator


class Group:
    __slots__ = "agent_ids"

    def __init__(self, agent_ids: Iterator[int]):
        """
        Create a group from the agent_ids
        :param agent_ids: The agent_ids
        """
        self.agent_ids = tuple(agent_ids)

    def combine(self, other) -> Group:
        """
        Combine this group with another one.
        :param other: The other group
        :return: The new group
        """
        i = 0
        j = 0
        n = len(self.agent_ids)
        m = len(other.agent_ids)
        new_ids = []
        while i < n and j < m:
            if self.agent_ids[i] < other.agent_ids[j]:
                new_ids.append(self.agent_ids[i])
                i += 1
            else:
                new_ids.append(other.agent_ids[j])
                j += 1
        while i < n:
            new_ids.append(self.agent_ids[i])
            i += 1
        while j < m:
            new_ids.append(other.agent_ids[j])
            j += 1
        return Group(new_ids)

    def __str__(self):
        return self.agent_ids.__str__()

    def __len__(self):
        return self.agent_ids.__len__()

    def __getitem__(self, item):
        return self.agent_ids.__getitem__(item)
