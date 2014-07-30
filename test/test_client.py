import datetime
import requests

from multiprocessing import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from server import run_forever
from pmp_api.pmp_client import Client
from pmp_api.core.auth import PmpAuth

from pmp_api.core.exceptions import NoToken


class TestPmpClient(TestCase):

    def setUp(self):
        self.server_process = Process(target=run_forever)
        self.server_process.start()
        self.test_url = 'http://127.0.0.1:8080/'
        self.test_entry_point = 'http://127.0.0.1:8080/?json_response=fixtures/homedoc.json'
        self.auth_url = self.test_url + 'auth/access_token?json_response=fixtures/authdetails.json'
        self.data_url = self.test_url + '?json_response=fixtures/test_data.json'

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)

    def test_home(self):
        client = Client(self.test_entry_point)
        values = requests.get(self.test_entry_point).json()
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        result = client.home()
        self.assertTrue(result)
        self.assertTrue(result.links)
        self.assertEqual(len(result.links), 7)

    def test_gain_access_find_correct_urn(self):
        client = Client(self.test_entry_point)
        values = requests.get(self.auth_url)
        with patch.object(PmpAuth, 'get_access_token2', return_value=values) as mocker:
            client.gain_access('client-id', 'client-secret')
            mocker.assert_called_with(self.auth_url)

    def test_get_without_connector_raise_no_auth_token(self):
        client = Client(self.test_url)
        with self.assertRaises(NoToken):
            client.get(self.test_url)

    def test_client_pager(self):
        client = Client(self.test_entry_point)
        values = requests.get(self.data_url).json()
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)
        self.assertNotEqual(client.pager, None)
        expected_values = {'next': "http://127.0.0.1:8080/docs?offset=20",
                           'prev': "http://127.0.0.1:8080/docs?",
                           'first': "http://127.0.0.1:8080/docs?",
                           'last': "http://127.0.0.1:8080/docs?offset=42920",
                           'current': "http://127.0.0.1:8080/docs?offset=10"}
        self.assertTrue(client.pager.navigable)
        self.assertEqual(client.pager.next, expected_values['next'])
        self.assertEqual(client.pager.prev, expected_values['prev'])
        self.assertEqual(client.pager.first, expected_values['first'])
        self.assertEqual(client.pager.last, expected_values['last'])
        self.assertEqual(client.pager.current, expected_values['current'])

    def test_get_makes_history(self):
        client = Client(self.test_entry_point)
        values = requests.get(self.data_url).json()
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector

        # current page should be set to None until first request
        self.assertEqual(client.current_page, None)
        client.get(self.data_url)
        self.assertEqual(client.current_page, self.data_url)
        self.assertEqual(client.history, [])

        # History won't be collected until our second page
        client.get(self.test_url)
        self.assertNotEqual(client.history, [])
        self.assertEqual(client.history[-1], self.data_url)

        # History will empty if we request last page in history stack
        client.get(self.data_url)
        self.assertEqual(client.history, [])
        self.assertEqual(client.forward_stack, [self.test_url])

    def test_get_with_history_item(self):
        pass

    def test_get_makes_history_on_second_request(self):
        pass

    def test_query(self):
        # test that query method actually requests proper query url
        pass
        
    def test_next_requests_actual_next(self):
        # set up document/pager with pre-determined next
        # affirm that next requests next
        # test with pager as none
        # test with pager.prev as none
        pass

    def test_back(self):
        pass

    def test_forward(self):
        pass

