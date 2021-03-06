from unittest import TestCase
from unittest.mock import Mock, patch, call

import os
import datetime
import requests
from multiprocessing import Process

from pmp_api.core.conn import PmpConnector
from pmp_api.core.exceptions import BadRequest
from pmp_api.core.exceptions import ExpiredToken
from pmp_api.core.exceptions import EmptyResponse
from server import run


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
        # Live server testing with JSON responses
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixture_dir = os.path.join(current_dir, 'fixtures')
        self.auth_doc = os.path.join(self.fixture_dir, 'authdetails.json')
        entry_point = 'http://127.0.0.1:8080/?json_response={}'
        self.auth_url = entry_point.format(self.auth_doc)
        self.server_process = Process(target=run)
        self.server_process.start()

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)

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

    def test_reauthorize_raise_no_token(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() - self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        with self.assertRaises(ExpiredToken):
            pconn.reauthorize()

    def test_successful_reauthorize(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        self.assertTrue(pconn.reauthorize())

    def test_reauthorize_with_expired_token_renewal(self):
        """If the token is expired but there is an access_token_url
        provided, the PmpConnector object will attempt to authenticate
        against the url and auto-reset the access token.

        If the `reauthorize` method does attempt to reauthenticate, it
        should call the method `authorizer.get_access_token2`.
        """
        auth_vals = {'client_id': 'client-id',
                     'client_secret': 'client-secret',
                     'token_expires': datetime.datetime.utcnow() + self.delta,
                     'access_token': None,
                     'access_token_url': 'http://www.google.com'}
        authorizer = Mock(**auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertTrue(pconn.reauthorize())
            self.assertEqual(len(authorizer.mock_calls), 1)
            self.assertEqual(authorizer.mock_calls[0],
                             call.get_access_token2('http://www.google.com'))

    def test_reauthorize_live_server_response(self):
        from pmp_api.core.auth import PmpAuth
        authorizer = PmpAuth('client-id', 'client-secret')
        authorizer.access_token_url = self.auth_url
        connector = PmpConnector(authorizer)
        self.assertTrue(connector.reauthorize())


class TestPmpConnectorGet(TestCase):
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
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        attribs = {'ok': False, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(BadRequest):
                pconn.get("http://www.google.com")

    def test_simple_get(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            results = pconn.get("http://www.google.com")
            self.assertEqual(results, self.test_vals)

    def test_get_header_inspect(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            pconn.get("http://www.google.com")
            session.prepare_request.assert_called_with(self.signed_request)

    def test_get_with_no_json(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        attribs = {'ok': True, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(EmptyResponse):
                pconn.get("http://www.google.com")

    def test_get_with_reauthorize(self):
        """If the token is expired but there is an access_token_url
        provided, the PmpConnector object will attempt to authenticate
        against the url and auto-reset the access token.

        This test looks to see if the PmpConnector's authorizer has been
        called three times, including a call to `get_access_token2` in the
        middle, which only happens in that particular branch of the function.
        """
        auth_vals = {'client_id': 'client-id',
                     'client_secret': 'client-secret',
                     'access_token': False,
                     'access_token_url': 'http://www.google.com',
                     'token_expires': datetime.datetime.utcnow() + self.delta,
                     'sign_request.side_effect': [ExpiredToken, None]}
        authorizer = Mock(**auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            pconn.get("http://www.google.com")
            self.assertEqual(len(authorizer.mock_calls), 3)
            self.assertEqual(authorizer.mock_calls[1],
                             call.get_access_token2('http://www.google.com'))


class TestPmpConnectorPut(TestCase):

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

    def test_bad_put_response(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        attribs = {'ok': False, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(BadRequest):
                pconn.put("http://www.google.com", {'some': 'data'})

    def test_simple_put(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            results = pconn.put("http://www.google.com", {'some': 'data'})
            self.assertEqual(results, self.test_vals)

    def test_put_header_inspect(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            pconn.put("http://www.google.com", {'some': 'data'})
            session.prepare_request.assert_called_with(self.signed_request)

    def test_put_with_no_json(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        attribs = {'ok': True, 'json.side_effect': ValueError}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            with self.assertRaises(EmptyResponse):
                pconn.put("http://www.google.com", {'some': 'data'})

    def test_put_with_reauthorize(self):
        """If the token is expired but there is an access_token_url
        provided, the PmpConnector object will attempt to authenticate
        against the url and auto-reset the access token.

        This test looks to see if the PmpConnector's authorizer has been
        called three times, including a call to `get_access_token2` in the
        middle, which only happens in that particular branch of the function.
        """
        auth_vals = {'client_id': 'client-id',
                     'client_secret': 'client-secret',
                     'access_token': False,
                     'access_token_url': 'http://www.google.com',
                     'token_expires': datetime.datetime.utcnow() + self.delta,
                     'sign_request.side_effect': [ExpiredToken, None]}
        authorizer = Mock(**auth_vals)
        response = Mock(**self.attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            pconn.put("http://www.google.com", {'some': 'data'})
            self.assertEqual(len(authorizer.mock_calls), 3)
            self.assertEqual(authorizer.mock_calls[1],
                             call.get_access_token2('http://www.google.com'))


class TestPmpConnectorDelete(TestCase):

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

    def test_bad_delete_response(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        attribs = {'status_code': 200}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertFalse(pconn.delete('http://www.google.com'))

    def test_simple_delete(self):
        self.auth_vals['token_expires'] = datetime.datetime.utcnow() + self.delta
        authorizer = Mock(**self.auth_vals)
        pconn = PmpConnector(authorizer)
        attribs = {'status_code': 204}
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertTrue(pconn.delete('http://www.google.com'))

    def test_delete_with_reauthorize(self):
        """If the token is expired but there is an access_token_url
        provided, the PmpConnector object will attempt to authenticate
        against the url and auto-reset the access token.

        This test looks to see if the PmpConnector's authorizer has been
        called three times, including a call to `get_access_token2` in the
        middle, which only happens in that particular branch of the function.
        """
        auth_vals = {'client_id': 'client-id',
                     'client_secret': 'client-secret',
                     'access_token': False,
                     'access_token_url': 'http://www.google.com',
                     'token_expires': datetime.datetime.utcnow() + self.delta,
                     'sign_request.side_effect': [ExpiredToken, None]}
        attribs = {'status_code': 204}
        authorizer = Mock(**auth_vals)
        response = Mock(**attribs)
        session = Mock(**{'send.return_value': response,
                          'prepare_request.return_value': self.signed_request})
        pconn = PmpConnector(authorizer)
        with patch.object(requests, 'Session', return_value=session) as mocker:
            self.assertTrue(pconn.delete("http://www.google.com"))
            self.assertEqual(len(authorizer.mock_calls), 3)
            self.assertEqual(authorizer.mock_calls[1],
                             call.get_access_token2('http://www.google.com'))
