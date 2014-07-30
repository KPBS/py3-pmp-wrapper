import os
import json
import requests

from multiprocessing import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from server import run_forever
from pmp_api.pmp_client import Client
from pmp_api.core.auth import PmpAuth

from pmp_api.collectiondoc.navigabledoc import NavigableDoc
from pmp_api.core.exceptions import NoToken
from pmp_api.core.exceptions import BadQuery


class TestPmpClient(TestCase):

    def setUp(self):
        self.server_process = Process(target=run_forever)
        self.server_process.start()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.fixture_dir = os.path.join(current_dir, 'fixtures')
        self.test_url = 'http://127.0.0.1:8080/'
        entry_point = 'http://127.0.0.1:8080/?json_response={}'

        # For various navigation tests
        self.nav_values = {'next': "http://127.0.0.1:8080/docs?offset=20",
                           'prev': "http://127.0.0.1:8080/docs?",
                           'first': "http://127.0.0.1:8080/docs?",
                           'last': "http://127.0.0.1:8080/docs?offset=42920",
                           'current': "http://127.0.0.1:8080/docs?offset=10"}

        # Fixture locations
        self.home_doc = os.path.join(self.fixture_dir, 'homedoc.json')
        self.auth_doc = os.path.join(self.fixture_dir, 'authdetails.json')
        self.data_doc = os.path.join(self.fixture_dir, 'test_data.json')

        # Can also return JSON via these urls and testing server
        self.test_entry_point = entry_point.format(self.home_doc)
        self.auth_url = entry_point.format(self.auth_doc)
        self.data_url = entry_point.format(self.data_doc)

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)

    def test_home(self):
        client = Client(self.test_entry_point)
        with open(self.home_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        result = client.home()
        self.assertTrue(result)
        self.assertTrue(result.links)
        self.assertEqual(len(result.links), 7)

    def test_gain_access_find_correct_urn(self):
        client = Client(self.test_entry_point)
        with open(self.auth_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        expected_url = 'http://127.0.0.1:8080/auth/access_token?json_response'
        expected_url += '=fixtures/authdetails.json'
        with patch.object(PmpAuth, 'get_access_token2', return_value=values) as mocker:
            client.gain_access('client-id', 'client-secret')
            mocker.assert_called_with(expected_url)

    def test_get_without_connector_raise_no_auth_token(self):
        client = Client(self.test_url)
        with self.assertRaises(NoToken):
            client.get(self.test_url)

    def test_client_pager(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)
        self.assertNotEqual(client.pager, None)
        self.assertTrue(client.pager.navigable)
        self.assertEqual(client.pager.next, self.nav_values['next'])
        self.assertEqual(client.pager.prev, self.nav_values['prev'])
        self.assertEqual(client.pager.first, self.nav_values['first'])
        self.assertEqual(client.pager.last, self.nav_values['last'])
        self.assertEqual(client.pager.current, self.nav_values['current'])

    def test_get_makes_history(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector

        # current page should be set to None until first request
        self.assertEqual(client.current_page, None)
        client.get(self.data_url)
        self.assertEqual(client.current_page, self.data_url)
        self.assertEqual(client.history, [])

    def test_history_collected(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.current_page = self.data_url

        # History won't be collected until our second page
        client.get(self.test_url)
        self.assertNotEqual(client.history, [])
        self.assertEqual(client.history[-1], self.data_url)

    def test_load_last_page_in_history(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.current_page = self.test_entry_point
        client.history.append(self.data_url)
        client.get(self.data_url)
        self.assertEqual(client.history, [])
        self.assertEqual(client.forward_stack, [self.test_entry_point])

    def test_history_end2end(self):
        # Repeat the three previous tests as end-to-end test
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
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

    def test_query(self):
        # Repeat the three previous tests as end-to-end test
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_get = Mock(return_value=values)
        client.get = mock_get
        client.document = NavigableDoc(values)
        result = client.query('urn:collectiondoc:query:docs',
                              params={'tag': 'sometag'})
        self.assertTrue(result)
        self.assertEqual(len(client.document.items), 10)
        with self.assertRaises(BadQuery):
            client.query('urn:collectiondoc:query:docs',
                         params={'badtag': 'sometag'})

    def test_next(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.next()
            mock_get.assert_called_with(self.nav_values['next'])

    def test_prev(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.prev()
            mock_get.assert_called_with(self.nav_values['prev'])

    def test_first(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.first()
            mock_get.assert_called_with(self.nav_values['first'])

    def test_last(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.last()
            mock_get.assert_called_with(self.nav_values['last'])

    def test_back(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.current_page = self.test_entry_point
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.back()
            mock_get.assert_called_with(self.test_entry_point)

    def test_forward(self):
        client = Client(self.test_entry_point)
        with open(self.data_doc, 'r') as jfile:
            values = json.loads(jfile.read())
        mock_connector = Mock(**{'get.return_value': values})
        client.connector = mock_connector
        client.current_page = self.test_entry_point
        client.history.append(self.data_url)
        client.get(self.data_url)

        with patch.object(Client, 'get') as mock_get:
            client.forward()
            mock_get.assert_called_with(self.test_entry_point)
