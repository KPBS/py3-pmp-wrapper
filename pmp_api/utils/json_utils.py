"""JSON utilities module:

This module includes functions for parsing nested
dictionaries returned from JSON.
"""
from itertools import dropwhile


class SearchResultsAmbiguous(Exception):
    pass


class NoResult(Exception):
    pass


def qfind(results, key):
    """
    Recursive method for finding nested dictionaries anywhere in a dictionary
    given a key which may or may not be in the dictionary.

    Arguments:
    results -- dictionary (could be nested)
    key -- dictionary key :: string that is searched for

    returns:
    generator of objects that contain the key
    """
    if isinstance(results, list):
        for item in results:
            yield from qfind(item, key)
    elif isinstance(results, dict):
        if key in results and isinstance(results[key], dict):
            yield results
            yield from qfind(results[key], key)
        elif key in results:
            yield results
        elif isinstance(results, dict):
            for k in results:
                yield from qfind(results[k], key)


def filter_dict(results, key, val):
    """
    Relies on qfind method to search out a particular value
    inside the dictionary. Not as efficient as `get_dict_from_unique_val`
    but works if you don't know the keys (in order) needed to find the
    values you are looking for.

    Arguments:
    results -- dictionary or list of dictionaries
    key -- key::string that gets val searched for
    val -- value::string searched for

    returns:
    filter object of results
    """
    qresults = qfind(results, key)

    def filterfunc(somedict):
        if key in somedict and val in somedict[key]:
            return True
        elif key in somedict and somedict[key] == val:
            return True
        return False
    return filter(filterfunc, qresults)


def returnfirst(func):
    """
    This decorator drops all results but the first from a generator
    object.
    """
    def inner(*args, **kwargs):
        try:
            result, *_ = func(*args, **kwargs)
            return result
        except ValueError:
            errmsg = "Result empty for provided arguments: {} {}"
            raise NoResult(errmsg.format(args, kwargs))
    return inner


@returnfirst
def get_dict(results, key, val):
    return filter_dict(results, key, val)
