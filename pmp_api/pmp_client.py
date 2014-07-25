"""
pmp_api.pmp_client module

``Pager`` -- for keeping track of PMP navigation links
``Client`` -- for easily making requests of PMP resources

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
    """The :class:`Pager <Pager>` object is for keeping track
    of navigation values from a PMP Hypermedia object. This object
    contains an :method update: method that looks for navigation
    links and updates :class:`Pager <Pager>` attributes.
    
    Usage::

      >>> from pmp_api.pmp_client import Pager
      >>> import requests
      >>> nav_page = requests.get("http://some-api.that-returns.json")
      >>> results = nav_page.json()
      >>> pager = Pager(results)
      >>> pager.navigable
      True
      >>> pager._next
     "http://some-api.that-returns.json/some-next-page-of-results"

    """
    def __init__(self):
        self._prev = None
        self._next = None
        self._last = None
        self._first = None
        self._current = None
        self.navigable = False

    def navigator(self, navigable_dict):
        """:method::navigator(navigable_dict)
        Returns navigable_dictionary object which can be searched
        against common navigation values in order to populate class
        attributes.
        """
        def _get_page(val):
            try:
                return next(filter_dict(navigable_dict, 'rels', val))['href']
            except StopIteration:
                return None
        return _get_page

    def update(self, result_dict):
        """:method:`updated` upadtes all page attributes as well as `navigable` boolean
        attribute.
        """
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

    def __repr__(self):
        return "<Pager for: {}>".format(self._current)


class Client(object):
    def __init__(self):  # , client_id, client_secret, entry_point):
        # self.entry_point = entry_point
        self.pager = None
        self.recent_result = {}
        # self.connector = self._get_access(client_id, client_secret)
        self.history = []
        self.forward_stack = []
        self.current_page = None

    def home(self):
        self.get(self.entry_point)

    def _get_access(self, client_id, client_secret):
        resp = requests.get(self.entry_point)
        home_doc = resp.json()
        # get_dict is fragile, but we want to know if this urn is not present.
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
        if self.pager is None:
            self.pager = Pager()
        self.pager.update(result_set)
        self.recent_result = result_set
        return recent_result

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
        elif len(self.history) > 1 and self.history[-1] == endpoint:
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
            if self.pager._next is not None:
                return self.get(self.pager._next)

    def prev(self):
        if self.pager and self.pager.navigable:
            if self.pager._prev is not None:
                return self.get(self.pager._prev)

    def last(self):
        if self.pager and self.pager.navigable:
            if self.pager._last is not None:
                return self.get(self.pager._last)

    def first(self):
        if self.pager and self.pager._first is not None:
            return self.get(self.pager._first)

    def back(self):
        if len(self.history) < 1:
            return
        else:
            self.get(self.history[-1])

    def forward(self):
        if len(self.forward_stack) < 1:
            return
        else:
            self.get(self.history[-1])
