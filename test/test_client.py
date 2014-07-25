import datetime
import requests

from unittest import TestCase
from unittest.mock import Mock, patch

from pmp_api.pmp_client import Client
from pmp_api.core.pmp_exceptions import ExpiredToken
from pmp_api.core.pmp_exceptions import EmptyResponse

### For reference only

class TestPmpConnector(TestCase):

    def setUp(self):
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
        self.test_vals = {'a': 1, 'b': 2, 'c': 'VALUE'}
        self.attribs = {'ok': True, 'json.return_value': self.test_vals}

    def test_bad_response(self):
        # Shouldn't raise EmptyResponse. Should return None
        attribs = {'ok': False, 'json.side_effect': ValueError}
        authorizer = Mock(**self.auth_vals)
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                               'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertEqual(pconn.get("http://www.google.com"), None)

    def test_simple_get(self):
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            results = pconn.get("http://www.google.com")
            self.assertEqual(results, self.test_vals)

    def test_get_header_inspect(self):
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            pconn.get("http://www.google.com")
            session.prepare_request.assert_called_with(self.signed_request)

    def test_get_with_no_json(self):
        attribs = {'ok': True, 'json.side_effect': ValueError}
        authorizer = Mock(**self.auth_vals)
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(EmptyResponse):
                pconn.get("http://www.google.com")

    def test_get_with_expired_token(self):
        auth_vals = {'client_id': 'client-id',
                     'client_secret': 'client-secret',
                     'access_token': 'bd50df0000000000',
                     'access_token_url': None,
                     'sign_request.side_effect': ExpiredToken}
        authorizer = Mock(**auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(ExpiredToken):
                pconn.get("http://www.google.com")
