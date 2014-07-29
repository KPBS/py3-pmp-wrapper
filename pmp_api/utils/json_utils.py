"""JSON utilities module:

This module includes functions for parsing nested
dictionaries returned from JSON.
"""
from itertools import dropwhile


class SearchResultsAmbiguous(Exception):
    pass


class NoResult(Exception):
    pass


def qfind(json_dict, key):
    """Return generator of dicts filtered from *json_dict* that contain *key*.
    Recursive method for finding nested dictionaries anywhere in a dictionary
    given a key which may or may not be in the dictionary.

    :param json_dict: dictionary (could be nested with lists/dicts inside)
    :param key: string (JSON object key)
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
    """Returns a filter iterator from *json_dict* where results contain
    *key* - *val* matches. Relies on qfind method to search out a particular
    value inside the dictionary, so it works on nested dictionaries.

    :param json_dict: dictionary or list of dictionaries (from JSON)
    :param key: string value to search for inside *json_dict*
    :param val: value search for either *inside* value from key or
    exactly matching value.
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
    """:decorator returnfirst:: returnfirst(func)

    Return decorator that strips out all but the first result value from the
    function's invocation. Not safe if results are not guaranteed to appear.

    :params func: function that returns multiple results.
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
def get_dict(json_dict, key, val):
    """Returns first dictionary that matches *key* - *val*
    search. Unsafe if results are not guaranteed to appear.

    :param json_dict: dictionary or list of dictionaries (from JSON)
    :param key: string value to search for inside *json_dict*
    :param val: value search for either *inside* value from key or
    exactly matching value.
    """
    return filter_dict(json_dict, key, val)
