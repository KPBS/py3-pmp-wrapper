from unittest import TestCase
from unittest.mock import Mock, patch

import datetime
import requests

from pmp_api.core.conn import PmpConnector
from pmp_api.core.exceptions import BadRequest
from pmp_api.core.exceptions import ExpiredToken
from pmp_api.core.exceptions import EmptyResponse


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
        authorizer = Mock(**self.auth_vals)
        self.pconn = PmpConnector(authorizer)
        self.test_vals = {'a': 1, 'b': 2, 'c': 'VALUE'}
        self.attribs = {'ok': True, 'json.return_value': self.test_vals}

    def test_bad_response(self):
        # Shouldn't raise EmptyResponse. Should return None
        attribs = {'ok': False, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(BadRequest):
                self.pconn.get("http://www.google.com")

    def test_simple_get(self):
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            results = self.pconn.get("http://www.google.com")
            self.assertEqual(results, self.test_vals)

    def test_get_header_inspect(self):
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.pconn.get("http://www.google.com")
            session.prepare_request.assert_called_with(self.signed_request)

    def test_get_with_no_json(self):
        attribs = {'ok': True, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(EmptyResponse):
                self.pconn.get("http://www.google.com")

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
        pconn = self.pconn
        pconn.authorizer = authorizer
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(ExpiredToken):
                pconn.get("http://www.google.com")

    def test_authorized_no_token(self):
        now = datetime.datetime.utcnow()
        future_expiry = now + datetime.timedelta(hours=1)
        auth_vals = {'access_token': None,
                     'token_expires': future_expiry}
        auth = Mock(**auth_vals)
        connector = PmpConnector(auth)
        self.assertFalse(connector.authorized)

    def test_authorized_token_expired(self):
        now = datetime.datetime.utcnow()
        past_expiry = now + datetime.timedelta(hours=1)
        auth_vals = {'access_token': None,
                     'token_expires': past_expiry}
        auth = Mock(**auth_vals)
        connector = PmpConnector(auth)
        self.assertFalse(connector.authorized)

    def test_authorized_should_be_authorized(self):
        now = datetime.datetime.utcnow()
        future_expiry = now + datetime.timedelta(hours=1)
        auth_vals = {'access_token': 'SOME VAL',
                     'token_expires': future_expiry}
        auth = Mock(**auth_vals)
        connector = PmpConnector(auth)
        self.assertTrue(connector.authorized)

    # def test_get_with_expired_token_make_request(self):
    #     auth_vals1 = {'client_id': 'client-id',
    #                   'client_secret': 'client-secret',
    #                   'access_token': 'bd50df0000000000',
    #                   'access_token_url': 'http:://www.google.com',
    #                   'sign_request.side_effect': ExpiredToken}
    #     auth_vals2 = auth_vals1.copy()
    #     auth_vals2['sign_request.side_effect'] = None
    #     auth_vals2['sign_request.return_value'] = self.signed_request
    #     auth_vals2['access_token'] = 'SECOND TRY TOKEN'
    #     authorizer1 = Mock(**auth_vals1)
    #     response = Mock(**self.attribs)
    #     session = Mock(**{'send.return_value': response,
    #                       'prepare_request.return_value': self.signed_request})
    #     pconn = self.pconn
    #     pconn.authorizer = authorizer1
    #     with patch.object(requests, 'Session', return_value=session) as mocker:
    #         pconn.get("http://www.google.com")
