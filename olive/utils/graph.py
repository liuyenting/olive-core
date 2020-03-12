"""
Graph data structures.
"""

from collections import deque


__all__ = ["DisjointSet", "Graph"]


class DisjointSet(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self._root = {node: node for node in nodes}
        self._rank = {node: 0 for node in nodes}

    def find(self, node):
        root = self._root[node]
        return node if root == node else self.find(root)

    def union(self, node1, node2):
        root1, root2 = self.find(node1), self.find(node2)
        if root1 == root2:
            return

        rank1, rank2 = self._rank[root1], self._rank[root2]
        if rank1 < rank2:
            self._root[root1] = root2
        elif rank1 > rank2:
            self._root[root2] = root1
        else:
            self._root[root1] = self._root[root2] = root1
            self._rank[root1] = self._rank[root2] = rank1 + 1

    ##

    @property
    def root(self):
        return self._root


class Graph(object):
    def __init__(self, nodes):
        self._nodes = nodes
        self._graph = {k: [] for k in nodes}

    def add_edges(self, parent, children):
        for child in children:
            self.add_edge(parent, child)

    def add_edge(self, parent, child):
        if parent not in self._graph:
            raise ValueError("unknown node")
        self._graph[parent].append(child)

    def find_path(self, start, end):
        """Use linear BFS to find an acyclic path."""
        paths = {start: [start]}
        q = deque(start)
        while len(q):
            curr_node = q.popleft()
            for next_node in self._graph[curr_node]:
                if next_node not in paths:
                    paths[next_node] = paths[curr_node] + [next_node]
                    q.append(next_node)
        return paths[end]

    ##

    @property
    def nodes(self):
        return self._nodes
