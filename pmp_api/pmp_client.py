import requests

from .core.auth import PmpAuth
from .core.conn import PmpConnector
from .utils.json_utils import qfind
from .utils.json_utils import filter_dict
from .utils.json_utils import get_dict


class Client(object):
    def __init__(self, entry_point, client_id, client_secret):
        self.entry_point = entry_point
        self.connector = self._get_access(client_id, client_secret)

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

    def query_link_types(self, endpoint):
        values = self.connector.get(endpoint)
        for item in qfind(values, 'rels'):
            if 'title' in item:
                yield item['title'], item['rels']
            else:
                yield item['rels']
