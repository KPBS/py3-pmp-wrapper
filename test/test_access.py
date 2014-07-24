from unittest import TestCase
from unittest.mock import Mock, patch
import datetime
import requests

from pmp_api.core.pmp_exceptions import NoToken
from pmp_api.core.pmp_exceptions import ExpiredToken
from pmp_api.core.pmp_exceptions import BadRequest


class TestPmpAccess(TestCase):

    def setUp(self):
        from pmp_api.core.access import PmpAccess
        self.access = PmpAccess('username', 'password')
        self.test_url = "http://www.google.com"
        self.label = "test"

    def test_generate_credentials_called_with(self):
        url = "http://www.google.com"
        payload = {'label': "test",
                   'scope': "read",
                   'token_expires_in': "200000"}
        test_vals = {'client_id': 'client-id',
                     'client_secret':  'client-secret'}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            client_id, secret = self.access.generate_new_credentials(url,
                                                                     self.label)
            mocker.assert_called_with(url,
                                      auth=('username', 'password'),
                                      data=payload,
                                      allow_redirects=True,
                                      timeout=5.0)
            self.assertEqual(client_id, test_vals['client_id'])
            self.assertEqual(secret, test_vals['client_secret'])

    def test_generate_credentials_set_credentials(self):
        url = "http://www.google.com"
        payload = {'label': "test",
                   'scope': "read",
                   'token_expires_in': "200000"}
        test_vals = {'client_id': 'client-id',
                     'client_secret':  'client-secret'}
        response_vals = {'ok': True,
                         'json.return_value': test_vals}
        response = Mock()
        response.configure_mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            self.access.generate_new_credentials(url, self.label)
            self.assertEqual(self.access.client_id,
                             test_vals['client_id'])
            self.assertEqual(self.access.client_secret,
                             test_vals['client_secret'])
            self.assertEqual(self.access.expiration,
                             payload['token_expires_in'])

        response_vals['ok'] = False
        response.reset_mock()
        response.configure_mock(**response_vals)
        with patch.object(requests, 'post', return_value=response) as mocker:
            with self.assertRaises(BadRequest):
                self.access.generate_new_credentials(url, self.label)

    def test_remove_credentials(self):
        url = "http://www.google.com"
        response_good = {'status_code': 204}
        response = Mock(**response_good)
        with patch.object(requests, 'delete', return_value=response) as mocker:
            result = self.access.remove_credentials(url)
            mocker.assert_called_with(url,
                                      auth=('username', 'password'),
                                      allow_redirects=True)
            self.assertTrue(result)

    def test_remove_credentails_bad_return(self):
        url = "http://www.google.com"
        response_bad = {'status_code': 200}
        response = Mock(**response_bad)
        with patch.object(requests, 'delete', return_value=response) as mocker:
            with self.assertRaises(BadRequest):
                self.access.remove_credentials(url)
                mocker.assert_called_with(url,
                                          auth=('username', 'password'),
                                          allow_redirects=True)
