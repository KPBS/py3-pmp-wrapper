"""
.. module:: pmp_api.utils.json_utils
   :synopsis: Utilities for parsing PMP JSON values

This module includes functions for parsing nested dictionaries returned
by the PMP API
"""
from functools import wraps
from itertools import dropwhile


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


def returnfirst(func):
    """Decorator for retrieving the first value of any function that returns
    multiple values or an iterator with more than one value.

    This function returns None if no results may be found.

    Args:
       `func` -- function that returns iterator
    """
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            result, *_ = func(*args, **kwargs)
            return result
        except ValueError:
            return None
    return inner


def get_nested_val(somedict, keys):
    """Returns JSON value retrieved by following *known* keys.

    This function makes it easy to plumb the depths of a nested
    dict with using an iterable of keys and integers.

    It will go as deep as keys/indices exist and return None if it
    doesn't find one or if it runs into a value it can't parse.

    Usage::

       >>> some_dict = {'links': {'collection' : [{'a': 'b'}]}}
       >>> get_nested_val(some_dict, ['links', 'collection'])
       [{'a': 'b'}]
       >>> # with a list index
       >>> get_nested_val(some_dict, ['links', 'collection', 0, 'a'])
       'b'
    """
    if somedict is None or len(keys) < 1:
        return
    if len(keys) == 1:
        key = keys[0]
        if all((isinstance(key, int),
                isinstance(somedict, list))) and key < len(somedict):
            return somedict[key]
        elif isinstance(somedict, dict):
            return somedict.get(key, None)
    else:
        key, *keys = keys
        if all((isinstance(key, int),
                isinstance(somedict, list))) and key < len(somedict):
            return get_nested_val(somedict[key], keys)
        elif isinstance(somedict, dict):
            return get_nested_val(somedict.get(key, None), keys)


def search_with_keys(list_of_results, keys, val):
    """If we have a set of keys we'd like to use to access
    an object and we have a particular value we are looking for,
    then we can filter a list of results in order to find the object
    that has the match for those keys and that value.

    This function returns a filter iterator that contains all matching
    results for the list of keys passed in and the val passed in.

    Args:

       `list_of_results` -- List of dictionaries from JSON
       `keys` -- tuple or list of keys to navigate the object
       `val` -- Matching value we're looking for

    Usage::

       >>> some_dict = {'links': {'collection' : [{'a': 'b'}]}}
       >>> list(search_with_keys(some_dict, ['links', 'collection', 0, 'a'], 'b'))
       [{'a': 'b'}]
    """
    def filter_nested_val(json_result):
        *head_keys, last_key = keys
        retrieved = get_nested_val(json_result, head_keys)
        if retrieved is not None and retrieved[last_key]:
            return retrieved[last_key] == val
    return filter(filter_nested_val, list_of_results)


def set_value(json_results, keys, newvalue):
    """If you have a set of key and/array indices that conform
    to a nested JSON object, you can use this function to set
    the value retrieved by those keys.

    Args:

       `json_results` -- Nested JSON Object
       `keys` -- tuple or list of keys to navigate the object
       `newvalue` -- Replacement value

    Usage::

       >>> some_dict = {'links': {'collection' : [{'a': 'b'}]}}
       >>> set_value(some_dict, ['links', 'collection', 0, 'a'], 'c')
       True
       >>> some_dict
       {'links': {'collection' : [{'a': 'c'}]}}

    It is also possible to write a find-and-replace by combining
    `set_value` with `search_with_keys`::

        >>> for items in search_keys(json_results, keys, searchval):
        ...  set_value(item, keys, newval)


    Returns: json_results passed in
    """
    *keys, last_key = keys
    editable = get_nested_val(json_results, keys)
    if editable is not None and editable.get(last_key, False):
        editable[last_key] = newvalue
        return editable
