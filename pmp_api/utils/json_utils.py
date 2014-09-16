"""
.. module:: pmp_api.utils.json_utils
   :synopsis: Utilities for parsing PMP JSON values

This module includes functions for parsing nested dictionaries returned
by the PMP API
"""
from functools import wraps


def qfind(json_dict, key):
    """Return generator of dicts filtered from `json_dict` that contain `key`.
    Recursive method for finding nested dictionaries anywhere in a dictionary
    given a key which may or may not be in the dictionary.

    This function actually returns the `parent` dictionary that contains a
    particular key. Consider the following example::

      >>> somedict = {'1': 1, '2': '2', 'a' : { '3' : 3}}
      >>> next(qfind(somedict, '2'))  # key present: returns whole thing
      {'2': '2', 'a': {'3': 3}, '1': 1}
      >>> next(qfind(somedict, '3'))
      {'3': 3}
      >>> next(qfind(somedict, '4'))
      Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
      StopIteration
      >>> list(qfind(somedict, '4'))
      []

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
        else:
            for k in json_dict:
                yield from qfind(json_dict[k], key)


def filter_dict(json_dict, key, val):
    """Returns a filter iterator from `json_dict` where results contain
    `key` - `val` matches.

    Args:
       `json_dict` -- JSON dictionary.
       `key` -- Key we are searching for.
       `val` -- Value that should explicitly match the key searched for.
    """
    qjson_dict = qfind(json_dict, key)

    def filterfunc(somedict):
        try:
            if somedict[key] == val or val in somedict[key]:
                return True
            else:
                return False
        except TypeError:
            # TypeError: if the val passed in is an int and
            # dict[key] is a string
            return False
    return filter(filterfunc, qjson_dict)
