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
    """If we have a set of objects, as well as keys we'd like to use to access
    each object, and we have a particular value we are looking for,
    then we can filter a list of results in order to find the object
    that has the match for those keys and that value.

    This function returns a filter iterator that contains all matching
    results for the list of keys passed in and the val passed in.

    Args:

       `list_of_results` -- List of dictionaries from JSON
       `keys` -- tuple or list of keys to navigate the object
       `val` -- Matching value we're looking for

    Usage::

       >>> some_dicts = [{'links': {'collection' : [{'a': 'b'}]}}
       ...    {'links': {'collection': [{'b': 'c'}]}}]
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
    the value retrieved by those keys for that particular JSON object.

    Args:

       `json_results` -- Nested JSON Object
       `keys` -- tuple or list of keys to navigate the object
       `newvalue` -- Replacement value

    Usage::

       >>> some_dict = {'links': {'collection' : [{'a': 'b'}]}}
       >>> set_value(some_dict, ['links', 'collection', 0, 'a'], 'c')
       [{'a': 'c'}]

    It is also possible to write a find-and-replace by combining
    `set_value` with `search_with_keys` to be used on lots of JSON objects::

        >>> for items in search_keys(json_results, keys, searchval):
        ...  set_value(item, keys, newval)


    Returns:
       Edited dictionary
    """
    *keys, last_key = keys
    editable = get_nested_val(json_results, keys)
    if editable is not None and editable.get(last_key, False):
        editable[last_key] = newvalue
        return editable


def reverse_result(func):
    """The recursive function `get_path` returns results in order reversed
    from desired. This decorator just reverses those results before returning
    them to caller.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            return result[::-1]
    return inner


@reverse_result
def get_path(json_result, key, path=None):
    """Find first occurrence of a key inside a nested dictionary. This is helpful
    only for unique keys across all nested brances of a dictionary and will
    return confusing results for dictionaries that do not conform to this rule.

    Returns list of results::

       >>> content =
       ...  {'attributes':
       ...      {'contentencoded': None, 'tags': [None], 'published': None,
       ...       'contenttemplated': None, 'title': None, 'guid': inf,
       ...       'description': None, 'byline': None, 'teaser': None},
       ...       'version': None, 'links': {'collection': [inf], '
       ...        item': [None],
       ...        'profile': [{'href': 'https://api-sandbox.pmp.io/profiles/story'}]}
       ...   'links' : [{'creator': 'https://someurl'}]
       ...     }
       >>> get_path(content, 'attributes')
       ['attributes']
       >>> get_path(content, 'tags')
       ['attributes', 'tags']
       >>> get_path(conent, 'creator')
       ['links', 0, 'creator']

    Args:

       `json_result` -- nested JSON dictionary values
       `key` -- key whose path we'd like to discover

    Kwargs:

       `path` -- The path gets built on recursive calls.

    This function is only valid for unique keys. Use generator `gen_path` to
    find all routes to a particular key inside a JSON object.
    """
    if path is None:
        path = []
    if isinstance(json_result, int) or isinstance(json_result, str):
        path = []
        return path
    elif isinstance(json_result, dict):
        for k, v in json_result.items():
            if key == k:
                path.append(key)
                return path
            else:
                result = get_path(v, key, path)
                if result:
                    path.append(k)
                    return path
    elif isinstance(json_result, list):
        for idx, item in enumerate(json_result):
            result = get_path(item, key, path)
            if result:
                path.append(idx)
                return path


def count_key(json_result, key):
    """Recursive method for counting the appearance of a particular key
    inside a nested JSON object. This was created mostly to make sure that the
    generator below stays honest.

    Args:

       `json_result` -- JSON object
       `key` -- Key to count

    Returns:

        Generator object that can be summed to get a complete count::

       >>> sum(count_key(JSON_OBJECT, "someKey"))
       10

    """
    if isinstance(json_result, dict):
        for k, v in json_result.items():
            if key == k:
                yield 1
            else:
                yield from count_key(v, key)
    elif isinstance(json_result, list):
        for item in json_result:
            yield from count_key(item, key)


def gen_path(json_result, key, path=None):
    """Generator function for introspecting a nested JSON object and finding all
    routes to a particular key. If, for instance, the key 'href' appears inside
    the JSON object 11 times, this generator will return 11 separate results,
    representing pathways to those 11 results.

    These pathways can be returned with `get_nested_val` or the data at at
    their endpoints can be edited with `set_value`.

    Args:

       `json_result` -- JSON object
       `key` -- Key to find routes for

    Returns:

       Generator of lists that each represent one path to the key passed in.

    Usage::

       >>> list(find_value(some_nested_json, 'SOMEKEY'))
       [['key1, 'key2', key3']['another_object', 'another_key', 1']]
       >>> get_nested_valu(some_nested_json, ['key1, 'key2', key3'])
       'SOMEVALUE'

    """
    if path is None:
        path = []
    if isinstance(json_result, dict):
        for k, v in json_result.items():
            if key == k:
                current_path = path[:]
                current_path.append(key)
                yield current_path
            else:
                current_path = path[:]
                current_path.append(k)
                yield from gen_path(v, key, path=current_path)

    elif isinstance(json_result, list):
        for idx, item in enumerate(json_result):
            current_path = path[:]
            current_path.append(idx)
            yield from gen_path(item, key, path=current_path)


def find_value(json_result, value, path=None):
    """Generator function for finding various paths to the value passed in.
    This function can handle arrays or objects and will return indices for
    array values and string keys for dictionary keys accessed to find the
    value.

    Args:

       `json_result` -- JSON object
       `value` -- value to search for

    Returns:

       Generator of lists that each represent one path to the value searched for.

    Usage::

       >>> list(find_value(some_nested_json, 'SOMEVALUE'))
       [['key1, 'key2', key3']['another_object', 'another_key', 1']]
       >>> get_nested_value(some_nested_json, ['another_object', 'another_key', 1'])
       'SOMEVALUE'

    """
    if path is None:
        path = []
    if isinstance(json_result, dict):
        for k, v in json_result.items():
            current_path = path[:]
            current_path.append(k)
            if value == v:
                yield current_path
            else:
                yield from find_value(v, value, path=current_path)

    elif isinstance(json_result, list):
        for idx, item in enumerate(json_result):
            current_path = path[:]
            current_path.append(idx)
            yield from find_value(item, value, path=current_path)
    else:
        if json_result == value:
            return path


def find_matching_pair(json_result, key, value):
    pass
