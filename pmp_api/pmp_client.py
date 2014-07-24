"""
pmp_api.pmp_client module

`Pager` -- for keeping track of PMP navigation links
`Client` -- for easily making requests of PMP resources

The Client module exists to facilitate making requests of the PMP API. It
supports following navigation elements as well as 'forward' and 'back'
functionality, similar to a browser.
"""

import requests

from .core.auth import PmpAuth
from .core.conn import PmpConnector
from .core.pmp_exceptions import NoToken
from .utils.json_utils import qfind
from .utils.json_utils import filter_dict
from .utils.json_utils import get_dict


class Pager(object):
    def __init__(self):
        self._prev = None
        self._next = None
        self._last = None
        self._first = None
        self._current = None
        self.navigable = False

    def navigator(self, navigable_dict):
        def _get_page(val):
            try:
                return next(filter_dict(navigable_dict, 'rels', val))['href']
            except StopIteration:
                return None
        return _get_page

    def update(self, result_dict):
        nav = list(qfind(result_dict, 'navigation'))
        if len(nav) > 1:
            self.navigable = True
            navigator = self.navigator(nav)
            self._prev = navigator('prev')
            self._next = navigator('next')
            self._last = navigator('last')
            self._first = navigator('first')
            self._current = navigator('self')

    def __str__(self):
        return "<Pager for: {}>".format(self._current)


class Client(object):
    def __init__(self, entry_point, client_id, client_secret):
        self.entry_point = entry_point
        self.pager = None
        self.recent_result = {}
        self.connector = self._get_access(client_id, client_secret)
        self.history = []
        self.forward_stack = []
        self.current_page = None

    def _get_access(self, client_id, client_secret):
        resp = requests.get(self.entry_point)
        home_doc = resp.json()
        # get_dict is fragile: sure you want to use it?
        auth_schema = get_dict(home_doc,
                               'rels',
                               "urn:collectiondoc:form:issuetoken")
        access_token_url = auth_schema.get('href', None)
        authorizer = PmpAuth(client_id, client_secret)
        try:
            authorizer.get_access_token(access_token_url)
            self.connector = PmpConnector(authorizer)
            return self.connector
        except NoToken:
            print("No Token set. No requests without a token")
            # RAISE SOME ERROR

    def query_rel_types(self, endpoint=None):
        if endpoint is not None:
            values = self.connector.get(endpoint)
            self.last_result = values
        else:
            values = self.last_result

        for item in qfind(values, 'rels'):
            if 'title' in item:
                yield item['title'], item['rels']
            else:
                yield item['rels']

    def query_type_options(self, rel_type, endpoint=None):
        if endpoint is not None:
            values = self.connector.get(endpoint)
            self.last_result = values
        else:
            values = self.last_result

        options = get_dict(values, 'rels', rel_type)
        return options

    def _get(self, endpoint):
        """
        Lowever level _get has been separated so that it
        can manage updating pager on each request.

        This method knows nothing about the `history` and
        `forward_stack` attributes and calling it directly
        will result in those stacks losing track.
        """
        result_set = self.connector.get(endpoint)
        new_pager = Pager()
        new_pager.update(result_set)
        self.pager = new_pager
        self.recent_result = result_set

    def get(self, endpoint):
        """
        This method has been set-up to handle 'forward' and 'back'
        requests as well as navigation returned by a collection-doc,
        including 'next', 'prev', 'first', 'last'.

        As a result, it has a lower-level `_get` method, which
        updates the pager object that itself keeps track of
        navigation, while this method updates the `history` and
        `forward_stack` in order to be able to return those
        values when a user wants to go "back" and "foward"
        """
        if self.current_page is None:
            # our first request only should be None
            self.current_page = endpoint
            result_set = self._get(endpoint)
        elif (self.history) > 1 and self.history[-1] == endpoint:
            self.forward_stack.append(self.current_page)
            self.current_page = self.history.pop()
            result_set = self._get(self.current_page)
        else:
            self.history.append(self.current_page)
            self.current_page = endpoint
            result_set = self._get(endpoint)

        return result_set

    def next(self):
        if self.pager and self.pager.navigable:
            if self.pager.__next is not None:
                return self.get(self.pager._next)

    def prev(self):
        if self.pager and self.pager.navigable:
            if self.pager.__prev is not None:
                return self.get(self.pager._prev)

    def last(self):
        if self.pager and self.pager.navigable:
            if self.pager.__last is not None:
                return self.get(self.pager._last)

    def first(self):
        if self.pager and self.pager.__first is not None:
            return self.get(self.pager._first)

    def back(self):
        if len(self.history) < 1:
            return
        else:
            self.get(self.history[-1])

    def forward(self):
        if len(self.forward_stacky) < 1:
            return
        else:
            self.get(self.history[-1])
