"""
Utilities that facilitates package distribution and discovery.
"""
import importlib
import inspect
import logging
import pkgutil

__all__ = ["enumerate_namespace_classes"]

logger = logging.getLogger("olive.utils")


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
