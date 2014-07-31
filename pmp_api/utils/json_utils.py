"""
.. module:: pmp_api.utils.json_utils
   :synopsis: Utilities for parsing PMP JSON values

This module includes functions for parsing nested dictionaries returned
by the PMP API
"""
from functools import wraps
from itertools import dropwhile
from pmp_api.core.exceptions import NoResult


def qfind(json_dict, key):
    """Return generator of dicts filtered from `json_dict` that contain `key`.
    Recursive method for finding nested dictionaries anywhere in a dictionary
    given a key which may or may not be in the dictionary.

    Args:
       `json_dict` -- JSON dictionary.
       `key` -- Key we are searching for.
    """
    if isinstance(json_dict, list):
        for item in json_dict:
            yield from qfind(item, key)
    elif isinstance(json_dict, dict):
        if key in json_dict and isinstance(json_dict[key], dict):
            yield json_dict
            yield from qfind(json_dict[key], key)
        elif key in json_dict:
            yield json_dict
        elif isinstance(json_dict, dict):
            for k in json_dict:
                yield from qfind(json_dict[k], key)


def filter_dict(json_dict, key, val):
    """Returns a filter iterator from `json_dict` where results contain
    `key` - `val` matches. Relies on qfind method to search out a particular
    value inside the dictionary, so it works on nested dictionaries.

    Args:
       `json_dict` -- JSON dictionary.
       `key` -- Key we are searching for.
       `val` -- Value that should explicitly match the key searched for.
    """
    qjson_dict = qfind(json_dict, key)

    def filterfunc(somedict):
        if key in somedict and val in somedict[key]:
            return True
        elif key in somedict and somedict[key] == val:
            return True
        return False
    return filter(filterfunc, qjson_dict)


def returnfirst(func):
    """Decorator for retrieving the first value of any function that returns
    multiple values or an iterator with more than one value.

    Args:
       `func` -- function that returns iterator
    """
    @wraps
    def inner(*args, **kwargs):
        try:
            result, *_ = func(*args, **kwargs)
            return result
        except ValueError:
            errmsg = "Result empty for provided arguments"
            raise NoResult(errmsg.format(args, kwargs))
    return inner


# This is more trouble than it's worth probably.
# Currently not used anywhere
@returnfirst
def get_dict(json_dict, key, val):
    """Returns first dictionary that matches `key` - `val`
    search. Unsafe if results are not guaranteed to appear.

    Args:
       `json_dict` -- JSON dictionary.
       `key` -- Key we are searching for.
       `val` -- Value that should explicitly match the key searched for.
    """
    return filter_dict(json_dict, key, val)
