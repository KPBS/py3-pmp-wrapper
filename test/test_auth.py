from unittest import TestCase
from unittest.mock import Mock, patch
import datetime
import requests

from pmp_api.core.pmp_exceptions import NoToken
from pmp_api.core.pmp_exceptions import ExpiredToken
from pmp_api.core.pmp_exceptions import BadRequest


class TestPmpAuthRequestSigning(TestCase):

    def setUp(self):
        from pmp_api.core.auth import PmpAuth
        self.authorizer = PmpAuth('client-id', 'client-secret')
        self.test_url = "http://www.kpbs.com"
        self.authorizer.access_token_url = "http://www.google.com"
        self.delta = datetime.timedelta(hours=4)
        self.authorizer.token_expires = datetime.datetime.utcnow() + self.delta
        self.authorizer.token_issued = datetime.datetime.utcnow() - self.delta

    def test_request_signing_no_token(self):
        r = requests.Request('GET', self.test_url)
        with self.assertRaises(NoToken):
            self.authorizer.sign_request(r)

    def test_request_signing_expired_token(self):
        r = requests.Request('GET', self.test_url)
        token = 'bd50df0000000000'
        self.authorizer.access_token = token
        self.authorizer.token_expires -= self.delta + self.delta
        with self.assertRaises(ExpiredToken):
            self.authorizer.sign_request(r)

    def test_request_signing_token_header(self):
        token = 'bd50df0000000000'
        self.authorizer.access_token = token
        r = requests.Request('GET', self.test_url)
        returned_req = self.authorizer.sign_request(r)
        headers = returned_req.headers
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer ' + token)


class PmpAuthTestGetToken(TestCase):

    def setUp(self):
        from pmp_api.core.auth import PmpAuth
        self.authorizer = PmpAuth('client-id', 'client-secret')
        self.test_url = "http://www.google.com"
        self.time_format = "%Y-%m-%dT%H:%M:%S+00:00"
        self.token = 'bd50df0000000000'
        # Setting up mock times and expiration times
        self.delta = datetime.timedelta(hours=4)
        self.expiry = int(self.delta.seconds)
        token_expires = datetime.datetime.utcnow() + self.delta
        self.token_expires = token_expires.replace(microsecond=0)
        issued = datetime.datetime.utcnow() - self.delta
        self.token_issued = issued.replace(microsecond=0)

    def test_auth_headers(self):
        headers = self.authorizer._auth_header()
        expected = "Basic " + "Y2xpZW50LWlkOmNsaWVudC1zZWNyZXQ="
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], expected)

        # Asserting content-type is still set. This should be straightforward
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'],
                         'application/x-www-form-urlencoded')

    def test_get_token_no_endpoint(self):
        with patch.object(requests, 'post') as mocker:
            with self.assertRaises(BadRequest):
                self.authorizer.get_access_token()

    def test_get_token_with_endpoint(self):
        self.authorizer.access_token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.assertTrue(self.authorizer.get_access_token(endpoint=self.test_url))
            self.assertEqual(self.authorizer.access_token, self.token)

    def test_get_token_with_saved_url(self):
        self.authorizer.access_token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token()
            self.assertEqual(self.authorizer.access_token, self.token)

    def test_get_token_post_called_with(self):
        self.authorizer.access_token_url = "http://www.google.com"
        self.authorizer.access_token = self.token
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        headers = {'Authorization': "Basic Y2xpZW50LWlkOmNsaWVudC1zZWNyZXQ=",
                   'Content-Type': 'application/x-www-form-urlencoded'}
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token()
            mocker.assert_called_with("http://www.google.com",
                                      params={'grant_type': 'client_credentials'},
                                      headers=headers)

    def test_get_token_vals_issued(self):
        self.authorizer.access_token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token()
            self.assertEqual(self.authorizer.token_issued, self.token_issued)

    def test_get_token_vals_expiration(self):
        self.authorizer.access_token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token()
            self.assertEqual(self.authorizer.token_expires.replace(microsecond=0),
                             self.token_expires)

    def test_get_token_vals_access_token(self):
        self.authorizer.access_token_url = "http://www.google.com"
        self.authorizer.access_token = self.token
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            received_token = self.authorizer.get_access_token()
            self.assertEqual(self.authorizer.access_token, self.token)
            self.assertEqual(received_token, self.token)

    def test_get_token_missing_token(self):
        self.authorizer.access_token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'token_expires_in': self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            with self.assertRaises(NoToken):
                self.authorizer.get_access_token()

    def test_delete_access_token(self):
        self.authorizer.access_token_url = "http://www.google.com"
        self.authorizer.access_token = self.token
        headers = {'Authorization': "Basic Y2xpZW50LWlkOmNsaWVudC1zZWNyZXQ=",
                   'Content-Type': 'application/x-www-form-urlencoded'}
        response_good = {'status_code': 204}
        response_bad = {'status_code': 200}
        response = Mock()
        response.configure_mock(**response_good)
        with patch.object(requests, 'delete', return_value=response) as mocker:
            self.authorizer.delete_access_token()
            mocker.assert_called_with("http://www.google.com",
                                      headers=headers)
            self.assertTrue(self.authorizer.delete_access_token())

        response.reset_mock()
        response.configure_mock(**response_bad)
        with patch.object(requests, 'delete', return_value=response) as mocker:
            self.authorizer.delete_access_token()
            mocker.assert_called_with("http://www.google.com",
                                      headers=headers)
            self.assertFalse(self.authorizer.delete_access_token())

    def test_delete_access_token_no_url(self):
        self.authorizer.access_token = self.token
        self.authorizer.token_expires = datetime.datetime.utcnow() + self.delta
        self.authorizer.token_issued = datetime.datetime.utcnow() - self.delta
        response = Mock()
        with patch.object(requests, 'delete', return_value=response) as mocker:
            with self.assertRaises(BadRequest):
                self.authorizer.delete_access_token()

    # Test get_access_token2 tests are below. #
    def test_get_token2(self):
        token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token2(token_url)
            self.assertEqual(self.authorizer.access_token, self.token)

    def test_get_token2_post_called_with(self):
        token_url = "http://www.google.com"
        self.authorizer.access_token = self.token
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token2(token_url)
            mocker.assert_called_with("http://www.google.com",
                                      auth=('client-id', 'client-secret'),
                                      headers=headers)

    def test_get_token2_vals_issued(self):
        token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token2(token_url)
            self.assertEqual(self.authorizer.token_issued, self.token_issued)

    def test_get_token2_vals_expiration(self):
        token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.authorizer.get_access_token2(token_url)
            self.assertEqual(self.authorizer.token_expires.replace(microsecond=0),
                             self.token_expires)

    def test_get_token2_vals_access_token(self):
        token_url = "http://www.google.com"
        self.authorizer.access_token = self.token
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'access_token': self.token,
                     'token_expires_in':  self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            received_token = self.authorizer.get_access_token2(token_url)
            self.assertEqual(self.authorizer.access_token, self.token)
            self.assertEqual(received_token, self.token)

    def test_get_token2_missing_token(self):
        token_url = "http://www.google.com"
        issued = datetime.datetime.strftime(self.token_issued,
                                            self.time_format)
        test_vals = {'token_expires_in': self.expiry,
                     'token_issue_date': issued}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            with self.assertRaises(NoToken):
                self.authorizer.get_access_token2(token_url)
