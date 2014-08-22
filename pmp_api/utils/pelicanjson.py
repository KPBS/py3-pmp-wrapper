"""JSON is a recursive data structure, so this module has been created in
order to (hopefully) make JSON easier to deal with. Often, it's necessary to
explore a JSON object without knowing precisely where things are (in the case
of Hypermedia, for example). By creating a recursive data structure, we can
facilitate such tasks as retrieving key-value pairs, iterating through the
data structure, and searching for elements in the data structure.

There are limitations, however: no JSON structure that has keys deeper
than Python's recursion limit (default: 1000 stack frames) will work.
"""
import copy
import json
import collections


class PelicanJson(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))
        for key, value in self.store.items():
            if isinstance(value, dict):
                self.store[key] = PelicanJson(value)
            elif isinstance(value, list):
            #     self.store[key] = self._update_list(value)
            # else:
            #     self.store[key] = value
                temp_list = []
                for item in value:
                    if type(item) == dict:
                        temp_list.append(PelicanJson(item))
                    else:  # won't work for lists of lists of JSON
                        # will need a separate handle-lists for that.
                        temp_list.append(item)
                self.store[key] = temp_list

    def _update_from_list(self, somelist):
        temp_list = []
        for item in somelist:
            if isinstance(item, dict):
                temp_list.append(PelicanJson(item))
            elif isinstance(item, list):
                temp_list.append(self._update_from_list(item))
            else:
                temp_list.append(item)
        return temp_list

    def __repr__(self):
        return "<PelicanJson: {}>".format(str(self.store))

    def __str__(self):
        return str(self.store)

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __len__(self):
        """Counts all keys and subkeys nested in the object.
        """
        return sum(1 for k in iter(self))

    def __iter__(self):
        """Iterates through the entire tree and returns all nested keys.
        """
        for k, v in self.store.items():
            yield k
            if type(v) == type(self):
                yield from iter(v)
            elif type(v) == list:
                for item in v:
                    if type(item) == type(self):
                        yield from iter(v)

    def items(self, path=None):
        """Yields path-value pairs from throughout the entire tree.
        """
        for k, v in self.store.items():
            yield k, v
            if type(v) == type(self):
                yield from v.items()
            elif type(v) == list:
                for list_item in v:
                    if type(list_item) == type(self):
                        yield from list_item.items()

    def enumerate(self, path=None):
        """Iterate through the PelicanJson object yielding 1) the full path to
        each value and 2) the value itself at that path.
        """
        if path is None:
            path = []
        for k, v in self.store.items():
            current_path = path[:]
            current_path.append(k)

            if type(v) == type(self):
                yield from v.enumerate(path=current_path)
            elif type(v) == list:
                for idx, list_item in enumerate(v):
                    list_path = current_path[:]
                    list_path.append(idx)
                    if type(list_item) == type(self):

                        yield from list_item.enumerate(path=list_path)
                    else:
                        yield current_path, list_item
            else:
                yield current_path, v

    def keys(self):
        """Generator that iterates through the keys of the nested object same as
        `__iter__()`
        """
        # Rewrite in terms of `enumerate`
        yield from iter(self)

    def values(self):
        """Generator that returns values-only for the object.
        """
        # Rewrite in terms of `enumerate`
        yield from (v for k, v in self.items())

    def convert(self):
        """Converts the object back to a native Python object (a nested dictionary)
        that is equal to the object passed in.
        """
        data = {}
        for k, v in self.store.items():
            if type(v) == type(self):
                data[k] = v.convert()
            elif type(v) == list:
                temp_list = []
                for list_item in v:
                    if type(list_item) == type(self):
                        temp_list.append(list_item.convert())
                    else:
                        temp_list.append(list_item)
                listcopy = copy.deepcopy(temp_list)
                data[k] = listcopy
            else:
                data[k] = v
        return data

    def serialize(self):
        """Returns JSON serialization of the object.
        """
        return json.dumps(self.convert())

    def count_key(self, key):
        """Returns a sum of the number of times a particular key appears in the object.
        """
        return sum(1 for k, v in self.items() if k == key)

    def searchkey(self, searchkey):
        """Generator that returns the (various) paths for a particular key
        """
        for path, value in self.enumerate():
            *path, key = path
            if key == searchkey:
                yield path

    def saerchvalue(self, searchval):
        """Generator that returns the (various) paths for a particular value
        """
        for path, value in self.enumerate():
            if value == searchval:
                yield path

    def get_nested_value(self, path):
        """Retrieves nested value at the end of a path.
        """
        def valgetter(data, key):
            if len(path) <= 1:
                return data[key]
            else:
                key, *keys = path
                return valgetter(data[key], keys)

        return valgetter(self.store, path)

    def set_nested_value(self, path, newvalue):
        *keys, last_key = path
        if len(keys) > 0:
            editable = self.get_nested_value(keys)
            editable[last_key] = newvalue
        else:
            self.store[path] = newvalue

    def pluck(self, key, value):
        """Returns the parent object that contains a particular key-value pair
        """
        for path in self.keypath(key):
            if self.get_value(path) == value:
                yield path, value
