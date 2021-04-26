from typing import Iterator


class Group:

    def __init__(self, agent_ids: Iterator[int]):
        self.agent_ids = tuple(agent_ids)

    def combine(self, other):
        i = 0
        j = 0
        n = len(self.agent_ids)
        m = len(other.agent_ids)
        new_ids = []
        while len(new_ids) < n and len(new_ids) < m:
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
