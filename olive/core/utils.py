from collections import deque
from functools import wraps
import importlib
import inspect
import logging
import pkgutil
import time

__all__ = ["DisjointSet", "enumerate_namespace_classes", "retry", "Singleton"]

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logger.debug('new singleton object "{}" created'.format(cls))
        return cls._instances[cls]


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


def retry(exception, n_trials=3, delay=1, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exception (Exception or tuple): the exception(s) to check
        n_trials (int): number of trials
        delay (int): initial delay between retries in seconds
        backoff (int): backoff multiplier
        logger (Logger): logging module to use
    """

    def retry_func(func):
        """Create a retry decorator according to requirement."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            """The wrapped function."""
            remain, next_delay = n_trials, delay
            while remain > 1:
                try:
                    return func(*args, **kwargs)
                except exception:
                    if logger:
                        logger.warning(f"retry in {next_delay} seconds...")
                    time.sleep(next_delay)
                    next_delay *= backoff
                remain -= 1
            # last run
            return func(*args, **kwargs)

        return wrapped

    return retry_func


def iter_namespace(pkg_name):
    """
    Iterate over a namespace package.

    Args:
        pkg_name (type): namespace package to iterate over

    Returns:
        (tuple): tuple containing
            finder (FileFinder): module location
            name (str): fully qualified name of the found item
            is_pkg (bool): whether the found path is a package
    """
    return pkgutil.iter_modules(pkg_name.__path__, pkg_name.__name__ + ".")


def enumerate_namespace_classes(pkg, predicate=lambda x: True, with_pkg=False):
    """
    Iterate over namespace and list all classes filtered by predicate.

    Args:
        pkg (package): namespace package of intereset
        predicate (function): the predicate function

    Returns:
        (list): list of classes
    """
    logger.debug(f"filter over {pkg}.. ")
    klasses = []
    pkgs = iter_namespace(pkg)
    for _, name, is_pkg in pkgs:
        pkg = importlib.import_module(name)
        _klasses = []
        for _, klass in inspect.getmembers(pkg, inspect.isclass):
            if predicate(klass):
                _klasses.append(klass)
        logger.debug(f'"{name}" -> {len(_klasses)} class(es)')
        for klass in _klasses:
            if with_pkg:
                klasses.append((pkg, klass))
            else:
                klasses.append(klass)
            logger.debug(f".. {klass.__name__}")
    return klasses
