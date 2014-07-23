import requests

from .core.auth import PmpAuth
from .core.conn import PmpConnector
from .utils.json_utils import qfind
from .utils.json_utils import filter_dict
from .utils.json_utils import get_dict


class Pager(object):
    """
    This may not work; there may be multiplate nav objects...
    """
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


class PaginatedConnection(object):
    pass

class Client(object):
    def __init__(self, entry_point, client_id, client_secret):
        self.entry_point = entry_point
        self.connector = self._get_access(client_id, client_secret)
        self.pagers = {}

    def _get_access(self, client_id, client_secret):
        resp = requests.get(self.entry_point)
        home_doc = resp.json()
        auth_schema = get_dict(home_doc,
                               'rels',
                               "urn:collectiondoc:form:issuetoken")
        access_token_url = auth_schema['href']
        authorizer = PmpAuth(client_id, client_secret)
        authorizer.get_access_token(access_token_url)
        self.connector = PmpConnector(authorizer)
        return self.connector

    def query_rel_types(self, endpoint):
        values = self.connector.get(endpoint)
        for item in qfind(values, 'rels'):
            if 'title' in item:
                yield item['title'], item['rels']
            else:
                yield item['rels']

    def make_pager(self, result_set, key):
        new_pager = Pager()
        self.pagers[key] = new_pager
        new_pager.update(result_set)
        return new_pager
