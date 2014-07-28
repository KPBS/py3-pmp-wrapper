import requests
import os
import json
import datetime

from unittest import TestCase
from unittest.mock import Mock, patch

from pmp_api.pmp_client import Client
from pmp_api.core.exceptions import ExpiredToken
from pmp_api.core.exceptions import EmptyResponse


class TestPmpConnector(TestCase):

    def setUp(self):
        from pmp_api.core.conn import PmpConnector
        token = 'bd50df0000000000'
        header = {'Authorization': 'Bearer ' + token}
        header['Content-Type'] = 'application/vnd.collection.doc+json'
        self.delta = datetime.timedelta(hours=4)
        self.signed_request = Mock(**{'headers': header})
        self.auth_vals = {'client_id': 'client-id',
                          'client_secret': 'client-secret',
                          'access_token': token,
                          'access_token_url': None,
                          'token_issued': datetime.datetime.utcnow() - self.delta,
                          'sign_request.return_value': self.signed_request}
        authorizer = Mock(**self.auth_vals)
        self.pconn = PmpConnector(authorizer)
        self.test_vals = {'a': 1, 'b': 2, 'c': 'VALUE'}
        self.attribs = {'ok': True, 'json.return_value': self.test_vals}

    def test_good_init(self):
        # Shouldn't raise EmptyResponse. Should return None
        attribs = {'ok': False, 'json.side_effect': ValueError}
        authorizer = Mock(**self.auth_vals)
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                               'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertEqual(pconn.get("http://www.google.com"), None)

    def test_bad_init(self):
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            results = pconn.get("http://www.google.com")
            self.assertEqual(results, self.test_vals) 
        
    def test_get_access_find_auth_token(self):
        pass

    def test_get_access_find_auth_token(self):
        pass

    def test_get_access_find_auth_token(self):
        pass
